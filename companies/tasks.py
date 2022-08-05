from celery import shared_task
from datetime import date, timedelta

from applications.models import TariffApplication, ApplicationStatus
from auth_user.celery import app
from auth_user.tasks import send_email


@shared_task()
def deactivate_tariff():
    today = date.today()
    tariffs = TariffApplication.objects.filter(end_date=today, status=ApplicationStatus.ACCEPTED)
    for tariff in tariffs:
        new_tariff = TariffApplication.objects.filter(
            owner=tariff.owner,
            status=ApplicationStatus.NEW,
            start_date__gt=today).exists()
        if not new_tariff:
            send_email.delay(
                subject='Ваш тариф на BePro закончился',
                to_list=[tariff.owner.email],
                template_name='end_of_tariff_warning.html',
                context={}
            )


@app.task
def end_of_tariff_warning():
    days = 1
    end_date = date.today() + timedelta(days=days)
    tariffs = TariffApplication.objects.filter(end_date=end_date, status=ApplicationStatus.ACCEPTED)
    for tariff in tariffs:
        new_tariff = TariffApplication.objects.filter(
            owner=tariff.owner,
            status=ApplicationStatus.NEW,
            start_date__gt=end_date).exists()
        if not new_tariff:
            send_email.delay(
                subject='Ваш тариф на BePro заканчивается',
                to_list=[tariff.owner.email],
                template_name='end_of_tariff_warning.html',
                context={}
            )
