from datetime import date, timedelta
import requests

from django.db import transaction
from rest_framework import status

from .models import SubscriptionOrder, Subscription
from config.settings import ZARINPAL


class SubscriptionService:
    def __init__(self, request):
        self.payment_request_url = ZARINPAL['REQUEST_URL']
        self.payment_start_pay_url = ZARINPAL['START_PAY_URL']
        self.payment_verify_url = ZARINPAL['VERIFY_URL']
        self.merchant_id = ZARINPAL.get('MERCHANT_ID')
        self.callback_url = ZARINPAL.get('CALLBACK_URL')
        self.request = request
        self.sub_obj = self.get_sub_obj()

    def get_sub_obj(self):
        sub = Subscription.objects.filter(user=self.request.user)
        if not sub.exists():
            sub_obj = Subscription.objects.create(
                user=self.request.user,
                last_validation=date.today(), 
                expiration_date=date.today() - timedelta(days=1)
            )
        else:   
            sub_obj = sub.first()
        return sub_obj

    def create_payment_url(self, plan_obj):
        """
        return payment url by using subscription plan object,
        Return : payment_url:(str/None), error:(str/None)
        """
        order_obj = SubscriptionOrder.objects.create(
            user=self.request.user,
            plan=plan_obj,
        )

        data = {
            "merchant_id": self.merchant_id,
            "amount": str(plan_obj.price),
            "currency": "IRT",
            "callback_url": self.callback_url,
            "description": "Transaction description.",
            "metadata": {
                "order_id": str(order_obj.id),
            }
        }
        try:
            res = requests.post(self.payment_request_url, json=data, headers={'Accept': 'application/json'})
        except requests.exceptions.RequestException as e:
            return None , "zarinpal request failed"

        res = res.json()
        if res['data'].get('authority'):
            authority = res['data']['authority']
            SubscriptionOrder.objects.filter(pk=order_obj.id).update(authority=authority)
            return self.payment_start_pay_url + authority, None
        
        return None, "authority not found in response."

    def verify_payment(self, order_obj):
        """
        verifying payment request.
        Return: verified:bool, error:(str/None)
        """
        data = {
            "merchant_id": self.merchant_id,
            "amount": order_obj.plan.price,
            "authority": order_obj.authority,
        }
        try: 
            res = requests.post(self.payment_verify_url, json=data, headers={'Accept': 'application/json'})
        except requests.exceptions.RequestException as e :
            return False, "zarinpal request failed."
        
        response = res.json()
        code = response['data'].get('code')
        if code and code in (100, 101):
            order_obj.payment_response = response
            order_obj.ref_id = response['data']['ref_id']
            order_obj.save(update_fields=("payment_response", "ref_id",))
            return True, None
        
        return False, response['errors']

    @transaction.atomic
    def apply_subscription(self, sub_order_obj):
        """
        applying user subscription information after verify.
        """
        sub_duration = sub_order_obj.plan.duration 
        sub_obj = self.sub_obj
        new_sub_expiration_date = self.get_new_expiration_date(last_expiration_date=sub_obj.expiration_date, sub_duration=sub_duration)

        sub_order_obj.is_paid = True
        sub_order_obj.is_consumed = True
        sub_order_obj.save(update_fields=("is_paid", "is_consumed"))

        sub_obj.expiration_date = new_sub_expiration_date
        sub_obj.is_active = True
        sub_obj.last_validation = date.today()
        sub_obj.save(update_fields=("expiration_date", "is_active", "last_validation",))

        return True

    def get_new_expiration_date(self, last_expiration_date, sub_duration):
        """
        return sum of last expiration date and new subscription duration if user 
        already have subscription. else sum today's date and new subscription duration.
        """
        today = date.today()
        delta = timedelta(days=sub_duration)
        new_exp_date = (today + delta) if last_expiration_date <= today else (last_expiration_date + delta)
        return new_exp_date

    

