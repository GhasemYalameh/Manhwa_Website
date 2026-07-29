from datetime import date, timedelta
import json
from uuid import uuid4

from django.db.models import F
import requests

from .models import SubscriptionOrder, Subscription, SubscriptionPlan


class SubscriptionService:
    def __init__(self):
        self.authority_payment_url = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
        self.base_payment_url = "https://sandbox.zarinpal.com/pg/StartPay/"

    def create_payment_url(self, amount, order_id):
        data = {
            "merchant_id": str(uuid4()),
            "amount": str(amount),
            "currency": "IRT",
            "callback_url": "https://localhost/subscription/verify/",
            "description": "Transaction description.",
            "metadata": {
                "order_id": str(order_id),
            }
        }

        res = requests.post(self.authority_payment_url, json=data, headers={'Accept': 'application/json'})
        res = res.json()
        authority = res['data']['authority']
        SubscriptionOrder.objects.filter(pk=order_id).update(authority=authority)
        return self.base_payment_url + authority

    def apply_subscription(self, request, authority):
        """
        applying user subscription information after verify.
        """
        sub_order_obj = SubscriptionOrder.objects.filter(authority=authority).first()
        sub_duration = sub_order_obj.plan.duration
        sub_obj = Subscription.objects.filter(user=request.user).first()
        new_sub_expiration_date = self.get_new_expiration_date(last_expiration_date=sub_obj.expiration_date, sub_duration=sub_duration)

        sub_order_obj.is_paid = True
        sub_order_obj.save(update_fields=("is_paid",))

        sub_obj.expiration_date = new_sub_expiration_date
        sub_obj.is_subscriber = True
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

    

