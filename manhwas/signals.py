from django.db.models.signals import post_save
from django.dispatch import receiver

from manhwas.models import Chapter
from notifications.tasks import chapter_published_notification


@receiver(post_save, sender=Chapter)
def create_notif_when_chapter_created(sender, instance, created, **kwargs):
    if created:
        chapter_published_notification.delay(instance.id)
