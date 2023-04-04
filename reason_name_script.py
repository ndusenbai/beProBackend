import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection
from django.apps import apps


with connection.cursor() as cursor:
    cursor.execute('SELECT id, name FROM scores_reason WHERE is_auto=False')
    rows = cursor.fetchall()


Reason = apps.get_model(
    app_label='scores',
    model_name='Reason'
)

for row in rows:
    reason = Reason.objects.get(id=row[0])
    reason.name_ru = row[1]
    reason.save()


Reason.objects.filter(is_auto=True).update(name_ru='Опоздание')


