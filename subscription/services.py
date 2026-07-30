from datetime import date, timedelta
from uuid import uuid4
import requests

from .models import SubscriptionOrder, Subscription


class SubscriptionService:
    def __init__(self, request):
        self.payment_url = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
        self.payment_start_pay_url = "https://sandbox.zarinpal.com/pg/StartPay/"
        self.payment_verify_url = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
        self.request = request
        self.sub_obj = self.get_sub_obj()
        self.MERCHANT_ID = str(uuid4())

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
        return payment url by using subscription plan object
        """
        order_obj = SubscriptionOrder.objects.create(
            user=self.request.user,
            plan=plan_obj,
        )

        data = {
            "merchant_id": self.MERCHANT_ID,
            "amount": str(plan_obj.price),
            "currency": "IRT",
            "callback_url": "https://localhost/subscription/verify/",
            "description": "Transaction description.",
            "metadata": {
                "order_id": str(order_obj.id),
            }
        }

        res = requests.post(self.payment_url, json=data, headers={'Accept': 'application/json'})
        res = res.json()
        authority = res['data']['authority']
        SubscriptionOrder.objects.filter(pk=order_obj.id).update(authority=authority)
        return self.payment_start_pay_url + authority

    def verify_payment(self, order_obj):
        data = {
            "merchant_id": self.MERCHANT_ID,
            "amount": order_obj.plan.price,
            "authority": order_obj.authority,
        }
        res = requests.post(self.payment_verify_url, json=data, headers={'Accept': 'application/json'})
        response = res.json()
        if response['data']['code'] in (100, 101):
            order_obj.payment_response = response
            order_obj.ref_id = response['data']['ref_id']
            order_obj.save(update_fields=("payment_response", "ref_id",))
            return True, None

        else :
            return False, response['errors']

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
        sub_obj.save(update_fields=("expiration_date", "is_subscriber", "last_validation",))

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

    

