from rest_framework import status

from applications.models import TariffApplication
from tariffs.models import Tariff
from tariffs.serializers import MyTariffSerializer


def update_tariff_application(instance: Tariff, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def delete_tariff(instance: Tariff) -> None:
    instance.is_active = False
    instance.save()


def get_my_tariff(owner):
    last_tariff_app = TariffApplication.objects.filter(owner=owner).order_by('-end_date').first()
    if last_tariff_app:
        data = MyTariffSerializer(last_tariff_app).data
        return data, status.HTTP_200_OK
    return {'message': 'Нет оплаченных заявок'}, status.HTTP_403_FORBIDDEN
