import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# create a worker with manhwa_project name
app = Celery('manhwa_project')

# read all setting witch start with CELERY_ from settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# read all task.py file in all apps
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

