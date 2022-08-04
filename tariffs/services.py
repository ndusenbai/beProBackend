from dateutil.relativedelta import relativedelta

from rest_framework import status

from applications.models import TariffApplication, ApplicationStatus
from tariffs.models import Tariff, TariffPeriod
from tariffs.serializers import MyTariffSerializer


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

