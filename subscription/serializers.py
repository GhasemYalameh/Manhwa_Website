from dataclasses import fields
from datetime import date, timedelta

from django.db.models import QuerySet
from rest_framework import serializers

from subscription.models import Subscription, SubscriptionOrder, SubscriptionPlan


class GetSubscriptionPlanSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.filter(is_purchasable=True)
    )
    class Meta:
        model = SubscriptionOrder
        fields = ("plan",)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("user", "is_active", "last_validation", "expiration_date",)


class SubscriptionPlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ("id", "name", "duration", "price", )