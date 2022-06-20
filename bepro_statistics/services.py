from django.apps import apps

from bepro_statistics.models import StatisticObserver


def get_statistics_queryset(company):
    return apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.filter(company=company)


def create_statistic(serializer, user):
    employees_list = serializer.validated_data['employees']
    print(employees_list)
    del serializer.validated_data['employees']
    statistic = apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.create(company=user.selected_company, **serializer.validated_data)
    statistic_observers = [
        StatisticObserver(statistic=statistic, user=employee) for employee in employees_list
    ]
    StatisticObserver.objects.bulk_create(statistic_observers)
    return statistic
