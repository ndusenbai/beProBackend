from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework import status

from applications.models import TariffApplication, ApplicationStatus
from companies.models import Company
from tariffs.models import Tariff, TariffPeriod
from tariffs.serializers import MyTariffSerializer

User = get_user_model()


def update_tariff_application(instance: Tariff, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def delete_tariff(instance: Tariff) -> None:
    instance.is_active = False
    instance.save()


def get_my_tariff(owner):
    last_tariff_app = TariffApplication.objects.filter(owner=owner, status=ApplicationStatus.ACCEPTED).order_by('-end_date').first()
    if last_tariff_app:
        data = MyTariffSerializer(last_tariff_app).data
        return data, status.HTTP_200_OK
    return {'message': 'Нет оплаченных заявок'}, status.HTTP_403_FORBIDDEN


def prolongate_my_tariff(owner):
    last_tariff_app = TariffApplication.objects.filter(owner=owner, status=ApplicationStatus.ACCEPTED).order_by('-end_date').first()
    if last_tariff_app:
        start_date = last_tariff_app.end_date + relativedelta(days=1)
        end_date = None

        if last_tariff_app.period == TariffPeriod.MONTHLY:
            end_date = start_date + relativedelta(months=1)
        elif last_tariff_app.period == TariffPeriod.YEARLY:
            end_date = start_date + relativedelta(years=1)

        TariffApplication.objects.create(
            tariff=last_tariff_app.tariff,
            owner=owner,
            start_date=start_date,
            end_date=end_date,
            period=last_tariff_app.period,
        )
        return {'message': 'created'}, status.HTTP_200_OK
    return {'message': 'Нет оплаченных заявок'}, status.HTTP_403_FORBIDDEN


def change_my_tariff(owner, tariff, period):
    last_tariff_app = TariffApplication.objects.filter(owner=owner, status=ApplicationStatus.ACCEPTED).order_by('-end_date').first()
    if last_tariff_app:
        start_date = last_tariff_app.end_date + relativedelta(days=1)
        end_date = None

        if period == TariffPeriod.MONTHLY:
            end_date = start_date + relativedelta(months=1)
        elif period == TariffPeriod.YEARLY:
            end_date = start_date + relativedelta(years=1)

        TariffApplication.objects.create(
            tariff=tariff,
            owner=owner,
            start_date=start_date,
            end_date=end_date,
            period=period,
        )
        return {'message': 'created'}, status.HTTP_200_OK
    return {'message': 'Нет оплаченных заявок'}, status.HTTP_403_FORBIDDEN


def deactivate_my_tariff(owner):
    Company.objects.filter(owner=owner).update(is_active=False)


def check_if_tariff_over_soon(owner: User) -> bool:
    """
    return True if tariff is over soon
    """
    today = date.today()
    days_from_today = date.today() + timedelta(days=3)
    tariff = TariffApplication.objects.filter(
        end_date__gte=today,
        end_date__lte=days_from_today,
        owner=owner,
        status=ApplicationStatus.ACCEPTED).order_by('-end_date').first()
    if tariff:
        new_tariff = TariffApplication.objects.filter(
            owner=tariff.owner,
            status=ApplicationStatus.NEW,
            start_date__gt=tariff.end_date).exists()
        if new_tariff:
            return False
        else:
            return True
    else:
        return True
