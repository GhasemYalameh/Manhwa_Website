from celery import shared_task
import logging

from django.core.cache import cache
from django.db.models import F

from .models import Manhwa

logger = logging.getLogger(__name__)

@shared_task(name='manhwas.sync_pending_views')
def sync_pending_views():
    """
    sync pending views from redis to DB.
    """
    logger.info('Starting syncing pending views...')

    manhwa_ids = Manhwa.objects.values_list('id', flat=True)

    update_count = 0
    total_pending_views = 0

    for manhwa_id in manhwa_ids:
        counter_key = f'manhwa:{manhwa_id}:pending_views'
        pending_count = cache.get(counter_key)

        # if key not exist, continue
        if not pending_count or int(pending_count) <= 0:
            continue

        try:
            pending_count = int(pending_count)

            # update manhwa views count
            Manhwa.objects.filter(pk=manhwa_id).update(views_count=F('views_count') + pending_count)

            cache.delete(counter_key)
            update_count += 1
            total_pending_views += pending_count

            logger.info(f'Updated {pending_count} pending views for {manhwa_id}')

        except Exception as e:
            logger.error(f'got error while syncing pending views for {manhwa_id}: {str(e)}')

    logger.info(
        f'finished syncing pending views. {update_count} manhwas updated.'
        f'total pending views: {total_pending_views}'
    )
    return {
        'total_views': total_pending_views,
        'updated_manhwas': update_count,
    }
