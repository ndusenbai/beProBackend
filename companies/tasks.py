from celery import shared_task
from datetime import date
from django.apps import apps


@shared_task()
def deactivate_tariff():
    now_date = date.today()
    apps.get_model(
        app_label='companies',
        model_name='Company'
    ).objects.filter(
        is_active=True,
        owner__tariff_applications__end_date__lte=now_date,
        owner__tariff_applications__status=2
    ).update(is_active=False)
