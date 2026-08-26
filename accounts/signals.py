from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUser
from subscription.models import Subscription


@receiver(post_save, sender=CustomUser)
def create_notif_when_episode_created(sender, instance, created, **kwargs):
    if created:
        Subscription.objects.create(user_id=instance.id)