from celery import shared_task
from datetime import date, timedelta

from applications.models import TariffApplication, ApplicationStatus
from auth_user.celery import app
from auth_user.tasks import send_email
from companies.models import Company


@shared_task()
def deactivate_tariff():
    now_date = date.today()
    Company.objects.filter(
        is_active=True,
        owner__tariff_applications__end_date__lte=now_date,
        owner__tariff_applications__status=2
    ).update(is_active=False)


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
