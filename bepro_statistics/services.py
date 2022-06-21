from django.apps import apps
from datetime import datetime, date, timedelta
from bepro_statistics.models import StatisticObserver
from bepro_statistics.serializers import UserStatsSerializer


def get_statistics_queryset():
    return apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.order_by()


def create_statistic(serializer):
    employees_list = serializer.validated_data['employees']
    del serializer.validated_data['employees']
    statistic = apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.create(**serializer.validated_data)
    statistic_observers = [
        StatisticObserver(statistic=statistic, user=employee) for employee in employees_list
    ]
    StatisticObserver.objects.bulk_create(statistic_observers)
    return statistic


def get_user_statistic(user):
    first_day_of_week = date.today() - timedelta(days=date.today().weekday())
    last_day_of_week = first_day_of_week + timedelta(days=6)

    general_statistic_queryset = apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.filter(user=user, statistic_type=1)

    double_statistic_queryset = apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.filter(user=user, statistic_type=2)

    inverted_statistic_queryset = apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.filter(user=user, statistic_type=3)

    user_statistics_json = {}

    all_generals_list = []

    all_doubles_list = []

    all_inverts_list = []

    general_stats_name_json = {}

    double_stats_name_json = {}

    inverted_stats_name_json = {}

    for general_stat in general_statistic_queryset:
        general_queryset = apps.get_model(
            app_label='bepro_statistics',
            model_name='UserStatistic'
        ).objects.filter(
            user=user,
            weekday__range=[first_day_of_week, last_day_of_week],
            statistic_id=general_stat.id
        ).select_related('statistic').order_by('weekday')
        serializer = UserStatsSerializer(general_queryset, many=True)
        general_stats_name_json[general_stat.name] = serializer.data
    all_generals_list.append(general_stats_name_json)

    for double_stat in double_statistic_queryset:
        double_queryset = apps.get_model(
            app_label='bepro_statistics',
            model_name='UserStatistic'
        ).objects.filter(
            user=user,
            weekday__range=[first_day_of_week, last_day_of_week],
            statistic_id=double_stat.id
        ).select_related('statistic').order_by('weekday')
        serializer = UserStatsSerializer(double_queryset, many=True)

        double_stats_name_json[double_stat.name] = serializer.data
    all_doubles_list.append(double_stats_name_json)

    for inverted_stat in inverted_statistic_queryset:
        inverted_queryset = apps.get_model(
            app_label='bepro_statistics',
            model_name='UserStatistic'
        ).objects.filter(
            user=user,
            weekday__range=[first_day_of_week, last_day_of_week],
            statistic_id=inverted_stat.id
        ).select_related('statistic').order_by('weekday')
        serializer = UserStatsSerializer(inverted_queryset, many=True)

        inverted_stats_name_json[inverted_stat.name] = serializer.data
    all_inverts_list.append(inverted_stats_name_json)

    user_statistics_json['all_general_stats'] = all_generals_list
    user_statistics_json['all_double_stats'] = all_doubles_list
    user_statistics_json['all_inverted_stats'] = all_inverts_list

    return user_statistics_json
#
# def generate_statistics_plot():
#
#     pass
