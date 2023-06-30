import os
from celery.schedules import crontab
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('proj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'deactivate_tariff': {
        'task': 'companies.tasks.deactivate_tariff',
        'schedule': crontab(hour=23, minute=50),
    },
    'end_of_tariff_warning': {
        'task': 'companies.tasks.end_of_tariff_warning',
        'schedule': crontab(hour=11, minute=0),
    },
    'absence_check': {
        'task': 'timesheet.tasks.absence_check',
        'schedule': crontab(hour=23, minute=50),
    }
}
