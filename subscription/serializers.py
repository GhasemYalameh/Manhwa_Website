from rest_framework import serializers

from .models import Subscription, SubscriptionOrder, SubscriptionPlan


class GetSubscriptionPlanSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.filter(is_purchasable=True)
    )
    class Meta:
        model = SubscriptionOrder
        fields = ("plan",)


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscriber = serializers.SerializerMethodField()
    class Meta:
        model = Subscription
        fields = ("is_subscriber", "last_validation", "expiration_date",)

    def get_is_subscriber(self, obj):
        return obj.is_subscriber()


class SubscriptionPlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ("id", "name", "duration", "price", )


class SubscriptionOrderSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanListSerializer()
    class Meta:
        model = SubscriptionOrder
        fields = ('plan', 'is_paid', 'is_consumed', 'created_at',)
