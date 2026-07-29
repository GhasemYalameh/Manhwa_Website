from django.db.models import F
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from subscription.services import SubscriptionService

from .models import Subscription, SubscriptionOrder
from . import serializers as srlzr

from datetime import date, timedelta

class SubscriptionApi(APIView):
    def get(self, request):
        if not (request.user and request.user.is_authenticated):
            return Response('please authenticate', status=status.HTTP_401_UNAUTHORIZED)

        sub = Subscription.objects.filter(user=request.user)
        if not sub.exists():
            sub_obj = Subscription.objects.create(
                user=request.user,
                last_validation=date.today(), 
                expiration_date=date.today() - timedelta(days=1)
            )
        else:   
            sub_obj = sub.first()

        obj = srlzr.SubscriptionSerializer(sub_obj)
        return Response(obj.data, status=status.HTTP_200_OK)

    def post(self, request):
        # receiving plan id
        plan_serializer = srlzr.GetSubscriptionPlanSerializer(data=request.data)
        plan_serializer.is_valid(raise_exception=True)
        plan_obj = plan_serializer.validated_data['plan']

        sub_order_obj = SubscriptionOrder.objects.create(
            user=request.user,
            plan=plan_obj,
        )
        plan_price = plan_obj.price 
        sub_service = SubscriptionService()
        payment_url = sub_service.create_payment_url(amount=plan_price, order_id=sub_order_obj.id)

        return Response(payment_url)

@api_view(("GET",))
def subscription_verify(request):
    authority = request.GET.get('Authority')
    payment_status = request.GET.get('Status')
    sub_service = SubscriptionService()

    if payment_status and payment_status.lower() == 'ok':
        sub_service.apply_subscription(request, authority)
        return Response("your subscription verified successfully. ", status=status.HTTP_200_OK)

    return Response('subscription failed.')
