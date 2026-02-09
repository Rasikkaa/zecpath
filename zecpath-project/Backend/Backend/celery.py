import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

app = Celery('Backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Import tasks explicitly to ensure they're registered
from common import tasks

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
