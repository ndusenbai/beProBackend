from tariffs.models import Tariff


def update_tariff_application(instance: Tariff, data: dict):
    for key, value in data.items():
        if key == 'max_capacity':
            continue
        setattr(instance, key, value)
    instance.save()
