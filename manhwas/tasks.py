from celery import shared_task
import logging

from django.db.models import F
from django_redis import get_redis_connection

from .models import Manhwa, View

logger = logging.getLogger(__name__)

redis_con = get_redis_connection('default')


@shared_task(name='manhwas.sync_pending_views')
def sync_pending_views():
    """
    syncing cached views in redis to database.
    """
    logger.info('Starting syncing cached views...')

    manhwa_ids = Manhwa.objects.values_list('id', flat=True)
    update_count, total_viewers = 0, 0

    for manhwa_id in manhwa_ids:
        manhwa_viewers_key = f'manhwa:{manhwa_id}:users_id'

        # atomic process
        pipe = redis_con.pipeline()
        pipe.smembers(manhwa_viewers_key)
        pipe.scard(manhwa_viewers_key)
        pipe.delete(manhwa_viewers_key)
        results = pipe.execute()

        manhwa_viewers_id = [int(mvid) for mvid in results[0]]  # mvid (manhwa viewer id)
        manhwa_viewers_count = results[1]

        # if key is empty, continue
        if not manhwa_viewers_count or manhwa_viewers_count <= 0:
            continue

        try:
            view_objects = [View(manhwa_id=manhwa_id, user_id=uid) for uid in manhwa_viewers_id]

            # update manhwa views count
            Manhwa.objects.filter(pk=manhwa_id).update(views_count=F('views_count') + manhwa_viewers_count)

            # crete view objects
            View.objects.bulk_create(view_objects)

            update_count += 1
            total_viewers += manhwa_viewers_count

            logger.info(f'Increase +{total_viewers} views to manhwa id ({manhwa_id})')

        except Exception as e:
            logger.error(f'got error while syncing pending views for {manhwa_id}: {str(e)}')

    logger.info(f'finished syncing cached views. {update_count} manhwas updated.')
    logger.info(f'total cached views: {total_viewers}')

    return {
        'total_views': total_viewers,
        'updated_manhwas': update_count,
    }
