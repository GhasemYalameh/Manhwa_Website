from django.db import models

from accounts.models import CustomUser

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    duration = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='subscription')
    is_subscriber = models.BooleanField(default=False)
    last_validation = models.DateField() # last validation for trust of is_subscriber field
    expire_date = models.DateTimeField()


    creation_date = models.DateTimeField()



class SubscriptionOrder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscription_orders')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscription_orders')
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)




