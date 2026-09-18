from datetime import date

from django.db import models
from django.utils import timezone

from config.settings import AUTH_USER_MODEL


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    duration = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    is_purchasable = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    is_active = models.BooleanField(default=False)
    last_validation = models.DateField(default=timezone.now) # last validation for trust of is_subscriber field
    expiration_date = models.DateField(default=timezone.now)

    creation_date = models.DateTimeField(auto_now_add=True)

    def is_subscriber(self) -> bool:
        """
        checking of user subscription .
        """
        today = date.today()
        if self.user.is_staff : # active subscription for admin users
            return True
        if not self.is_active:
            return False
        if self.last_validation == today:  # if subscription is active and last validation is today
            return True

        self.last_validation = today
        if self.expiration_date >= today:
            self.save(update_fields=("last_validation",))
            return True

        self.is_active = False
        self.save(update_fields=("last_validation", "is_active",))
        return False


class SubscriptionOrder(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription_orders')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscription_orders')
    is_paid = models.BooleanField(default=False)
    is_consumed = models.BooleanField(default=False)

    authority = models.CharField(max_length=100, blank=True)
    payment_response = models.JSONField(null=True ,blank=True)
    ref_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)




