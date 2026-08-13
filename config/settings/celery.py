# ===================================
# Celery Configuration
# ===================================

CELERY_BROKER_URL = 'redis://redis:6379/1'
CELERY_RESULT_BACKEND = 'redis://redis:6379/1'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TIMEZONE = 'Asia/Tehran'

CELERY_TASK_TRACK_STARTED = True

CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# ===================================
# Celery Beat Schedule
# ===================================

CELERY_BEAT_SCHEDULE = {
    'sync-pending-views-every-5-minutes': {
        'task': 'manhwas.sync_pending_views',
        'schedule': 300.0,  # 5 minutes
    },
}
