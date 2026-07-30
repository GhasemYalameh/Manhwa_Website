from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from .services import SubscriptionService
from .models import SubscriptionOrder, SubscriptionPlan
from . import serializers as srlzr



class SubscriptionApi(APIView):
    permission_classes = [IsAuthenticated,]
    
    def get(self, request):
        sub_service = SubscriptionService(request)
        obj = srlzr.SubscriptionSerializer(sub_service.sub_obj)
        return Response(obj.data, status=status.HTTP_200_OK)

    def post(self, request):
        # receiving plan id
        plan_serializer = srlzr.GetSubscriptionPlanSerializer(data=request.data)
        plan_serializer.is_valid(raise_exception=True)
        plan_obj = plan_serializer.validated_data['plan']

        sub_service = SubscriptionService(request)
        payment_url = sub_service.create_payment_url(plan_obj)

        return Response(payment_url)

@api_view(("GET",))
def subscription_verify(request):
    authority = request.GET.get('Authority')
    payment_status = request.GET.get('Status')
    sub_service = SubscriptionService(request)

    if payment_status and payment_status.lower() == 'ok':
        order_obj = get_object_or_404(SubscriptionOrder, authority=authority, user=request.user)
        if order_obj.is_consumed == True:
            return Response("this subscription has been consumed.", status=status.HTTP_400_BAD_REQUEST)

        is_verified, errors = sub_service.verify_payment(order_obj)
        if not is_verified:
            return Response(errors)
        
        sub_service.apply_subscription(order_obj)
        return Response("your subscription verified successfully. ", status=status.HTTP_200_OK)
        
    
    return Response('subscription failed.')


@api_view(("GET",))
def subscription_plan_list(request):
    sub_plans = SubscriptionPlan.objects.filter(is_purchasable=True)
    serializer = srlzr.SubscriptionPlanListSerializer(sub_plans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)