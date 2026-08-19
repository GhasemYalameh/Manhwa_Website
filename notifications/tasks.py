from celery import shared_task
from django.db.models import Q
import logging

from manhwas.models import Episode, WatchList
from notifications.models import Notification

logger = logging.getLogger(__name__)

@shared_task(name='notifications.episode_published_notification')
def episode_published_notification(episode_id):
    """
    notifying users after publishing new episode who added the manhwa to his watch list.
    """
    logger.info('starting to create notification for episode publication...')

    episode_obj = Episode.objects.get(pk=episode_id)
    manhwa_id = episode_obj.manhwa_id
    curser = 0
    BACH_SIZE = 1000
    while True:
        rows = WatchList.objects.filter(
            Q(manhwa_id=manhwa_id) & ~Q(watching_status=WatchList.STOPPED),
            id__gt=curser
        ).order_by('id').values('user_id','id')[:BACH_SIZE]

        rows = list(rows)
        if not rows:
            break

        notif_objects = []
        for row in rows :
            notif_objects.append(
                Notification(
                    recipient_id=row['user_id'],
                    notif_type=Notification.EPISODE_PUBLISHED,
                    target_object=episode_obj
                )
            )
        Notification.objects.bulk_create(notif_objects, ignore_conflicts=True)
        curser = rows[-1]['id']

    logger.info('all notifications created.')
