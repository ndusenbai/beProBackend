from tariffs.models import Tariff


def update_tariff_application(instance: Tariff, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def delete_tariff(instance: Tariff) -> None:
    instance.is_active = False
    instance.save()
