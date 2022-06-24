from django.apps import apps
from datetime import datetime, date, timedelta
from bepro_statistics.models import StatisticObserver
from bepro_statistics.serializers import UserStatsSerializer
import matplotlib.pyplot as plt
import numpy as np


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
        generate_general_statistics_plot(serializer.data, general_stat.name)
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

        # HERE I'M GENERATING PLOT
        generate_double_statistics_plot(serializer.data, double_stat.name)
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
        # generate_inverted_statistics_plot(serializer.data, double_stat.name)

    all_inverts_list.append(inverted_stats_name_json)

    user_statistics_json['all_general_stats'] = all_generals_list
    user_statistics_json['all_double_stats'] = all_doubles_list
    user_statistics_json['all_inverted_stats'] = all_inverts_list

    return user_statistics_json


weekday_list = [0, 1, 2, 3, 4, 5, 6]
weekday_word_list = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']


def generate_general_statistics_plot(serializer, name):
    some_list = []

    some_dict = {}
    for s in serializer:
        some_dict[s['weekday_num']] = s['fact']

    for weekday in weekday_list:
        if weekday in some_dict:
            some_list.append(some_dict[weekday])
        else:
            some_list.append(0)

    ypoints = np.array(some_list)
    xpoints = np.array(weekday_list)
    plt.plot(xpoints, ypoints, marker='o')
    plt.savefig(f'{name}.png', bbox_inches='tight', dpi=100)
    plt.close()
    pass


def generate_inverted_statistics_plot(serializer, name):
    some_list = []

    some_dict = {}
    for s in serializer:
        some_dict[s['weekday_num']] = -abs(s['fact'])

    for weekday in weekday_list:
        if weekday in some_dict:
            some_list.append(some_dict[weekday])
        else:
            some_list.append(0)

    ypoints = np.array(some_list)
    xpoints = np.array(weekday_list)
    plt.plot(xpoints, ypoints, marker='o')
    plt.savefig(f'{name}.png', bbox_inches='tight', dpi=100)
    plt.close()
    pass


def generate_double_statistics_plot(serializer, name):
    some_list = []
    plan_list = []

    some_dict = {}
    for s in serializer:
        some_dict[s['weekday_num']] = s['fact']
        if not plan_list:
            plan_list.append(s['plan'])
    plan_list = plan_list * 7
    for weekday in weekday_list:
        if weekday in some_dict:
            some_list.append(some_dict[weekday])
        else:
            some_list.append(None)

    plt.plot(weekday_word_list, some_list, plan_list, marker='o')
    plt.title(f'{name}')
    plt.savefig(f'media/{name}.png', bbox_inches='tight', dpi=100)
    plt.close()
    pass


