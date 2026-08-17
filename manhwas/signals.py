from django.db.models.signals import post_save
from django.dispatch import receiver

from manhwas.models import Episode
from notifications.tasks import episode_published_notification


@receiver(post_save, sender=Episode)
def create_notif_when_episode_created(sender, instance, created, **kwargs):
    if created:
        episode_published_notification.delay(instance.id)
