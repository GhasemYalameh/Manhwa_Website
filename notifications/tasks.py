from celery import shared_task
from django.db.models import Q
import logging

from manhwas.models import WatchList
from notifications.models import Notification

logger = logging.getLogger(__name__)

@shared_task(name='notifications.episode_published_notification')
def episode_published_notification(episode_obj):
    """
    notifying users after publishing new episode who added the manhwa to his watch list.
    """
    logger.info('starting to create notification for episode publication...')

    manhwa_id = episode_obj.manhwa_id
    curser = 0
    BACH_SIZE = 1000
    while True:
        users_id = WatchList.objects.filter(
            Q(manhwa__id=manhwa_id) & \
            Q(watching_status=WatchList.STOPPED).negate(),
            id__gt=curser
        ).values_list('user_id', flat=True)[:BACH_SIZE]

        if not users_id:
            break

        notif_objects = []
        for user_id in users_id :
            notif_objects.append(
                Notification(
                    recipient=user_id,
                    notif_type=Notification.EPISODE_PUBLISHED,
                    target_object=episode_obj
                )
            )
        Notification.objects.bulk_create(notif_objects, ignore_conflicts=True)

    logger.info('all notifications created.')
