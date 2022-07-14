import matplotlib.pyplot as plt
import numpy as np
from typing import OrderedDict
from datetime import datetime, date, timedelta

from django.apps import apps
from django.db import IntegrityError
from django.db.transaction import atomic
from django.db.models import Q

from bepro_statistics.models import StatisticObserver, Statistic, UserStatistic, VisibilityType
from bepro_statistics.serializers import UserStatsSerializer, StatsForUserSerializer
from companies.models import Role, RoleChoices
from timesheet.models import TimeSheet


def get_statistics_queryset():
    return apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.order_by()


@atomic
def create_statistic(serializer):
    employees_list = serializer.validated_data['employees']
    del serializer.validated_data['employees']
    statistic = Statistic.objects.create(**serializer.validated_data)
    statistic_observers = [
        StatisticObserver(statistic=statistic, role=employee.role) for employee in employees_list
    ]
    StatisticObserver.objects.bulk_create(statistic_observers)
    return statistic


def get_user_statistic(user):
    first_day_of_week = date.today() - timedelta(days=date.today().weekday())
    last_day_of_week = first_day_of_week + timedelta(days=6)

    general_statistic_queryset = Statistic.objects.filter(role=user.role, statistic_type=1)

    double_statistic_queryset = Statistic.objects.filter(role=user.role, statistic_type=2)

    inverted_statistic_queryset = Statistic.objects.filter(role=user.role, statistic_type=3)

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
            role=user.role,
            day__range=[first_day_of_week, last_day_of_week],
            statistic_id=general_stat.id
        ).select_related('statistic').order_by('day')
        serializer = UserStatsSerializer(general_queryset, many=True)
        general_stats_name_json[general_stat.name] = serializer.data
        generate_general_statistics_plot(serializer.data, general_stat.name, user)
    all_generals_list.append(general_stats_name_json)

    for double_stat in double_statistic_queryset:
        double_queryset = apps.get_model(
            app_label='bepro_statistics',
            model_name='UserStatistic'
        ).objects.filter(
            role=user.role,
            day__range=[first_day_of_week, last_day_of_week],
            statistic_id=double_stat.id
        ).select_related('statistic').order_by('day')
        serializer = UserStatsSerializer(double_queryset, many=True)

        double_stats_name_json[double_stat.name] = serializer.data

        # HERE I'M GENERATING PLOT
        generate_double_statistics_plot(serializer.data, double_stat.name, user)
    all_doubles_list.append(double_stats_name_json)

    for inverted_stat in inverted_statistic_queryset:
        inverted_queryset = apps.get_model(
            app_label='bepro_statistics',
            model_name='UserStatistic'
        ).objects.filter(
            role=user.role,
            day__range=[first_day_of_week, last_day_of_week],
            statistic_id=inverted_stat.id
        ).select_related('statistic').order_by('day')
        serializer = UserStatsSerializer(inverted_queryset, many=True)

        inverted_stats_name_json[inverted_stat.name] = serializer.data
        generate_inverted_statistics_plot(serializer.data, inverted_stat.name, user)

    all_inverts_list.append(inverted_stats_name_json)

    user_statistics_json['all_general_stats'] = all_generals_list
    user_statistics_json['all_double_stats'] = all_doubles_list
    user_statistics_json['all_inverted_stats'] = all_inverts_list

    return user_statistics_json


weekday_list = [0, 1, 2, 3, 4, 5, 6]
weekday_word_list = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']


def generate_general_statistics_plot(serializer, name, user):
    some_list = []

    some_dict = {}
    for s in serializer:
        some_dict[s['day_num']] = s['fact']

    for weekday in weekday_list:
        if weekday in some_dict:
            some_list.append(some_dict[weekday])
        else:
            some_list.append(0)

    ypoints = np.array(some_list)
    xpoints = np.array(weekday_list)

    plt.plot(xpoints, ypoints, marker='o')
    plt.savefig(f'media/{name}-{user.full_name}.png', bbox_inches='tight', dpi=100)
    plt.close()
    pass


def generate_inverted_statistics_plot(serializer, name, user):
    some_list = []

    some_dict = {}
    for s in serializer:
        some_dict[s['day_num']] = -abs(s['fact'])

    for weekday in weekday_list:
        if weekday in some_dict:
            some_list.append(some_dict[weekday])
        else:
            some_list.append(0)

    ypoints = np.array(some_list)
    xpoints = np.array(weekday_list)
    plt.plot(xpoints, ypoints, marker='o')
    plt.savefig(f'media/{name}-{user.full_name}.png', bbox_inches='tight', dpi=100)
    plt.close()
    pass


def generate_double_statistics_plot(serializer, name, user):
    some_list = []
    plan_list = []

    some_dict = {}
    for s in serializer:
        some_dict[s['day_num']] = s['fact']
        if not plan_list:
            plan_list.append(s['plan'])
    plan_list = plan_list * 7
    for weekday in weekday_list:
        if weekday in some_dict:
            some_list.append(some_dict[weekday])
        else:
            some_list.append(None)
    plt.style.use('seaborn-whitegrid')
    plt.plot(weekday_word_list, some_list, plan_list, marker='o')
    plt.title(f'{name}')
    plt.savefig(f'media/{name}-{user.full_name}.png', bbox_inches='tight', dpi=100)
    plt.close()


@atomic
def create_user_statistic(role: Role, data: OrderedDict):
    last_check_in = TimeSheet.objects.filter(role=role, check_out__isnull=True).order_by('-day').first()
    UserStatistic.objects.create(
        role=role,
        statistic_id=data['statistic_id'],
        day=last_check_in.day,
        fact=data['fact'])


def check_user_permission(user, role):

    if user.role == role or user.role.role == RoleChoices.HR:
        return {"visibility__in": {VisibilityType.HIDDEN,
                                   VisibilityType.EMPLOYEES,
                                   VisibilityType.OPEN_DEPARTMENT,
                                   VisibilityType.OPEN_EVERYONE}}
    elif user.role.department == role.department:
        return {"visibility__in": {VisibilityType.OPEN_DEPARTMENT,
                                   VisibilityType.OPEN_EVERYONE,
                                   VisibilityType.EMPLOYEES}}
    elif user.role.company == role.company:
        return {"visibility__in": {VisibilityType.OPEN_EVERYONE,
                                   VisibilityType.EMPLOYEES}}
    else:
        return {}


def get_stats_for_user(request):

    role = Role.objects.get(id=request.query_params['role_id'])
    now = datetime.now()
    monday = date.today() - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    data = []

    visibility_level = check_user_permission(request.user, role)

    stats = Statistic.objects.filter((Q(department=role.department) | Q(role=role)) | Q(**visibility_level))
    for stat in stats:
        if not (stat.visibility == VisibilityType.EMPLOYEES and not request.user.role.
                observing_statistics.select_related('statistic').only('statistic').filter(statistic=stat)):
            user_stats = UserStatistic.objects \
                .filter(role=role, statistic=stat, day__range=[monday, sunday]) \
                .order_by('day')

            data.append(StatsForUserSerializer({'statistic': stat, 'user_statistics': user_stats}).data)

    return data


def get_history_stats_for_user(user, data: OrderedDict):

    role = Role.objects.get(id=data['role_id'])
    stat_types = data['statistic_types']
    visibility_level = check_user_permission(user, role)

    stats = Statistic.objects.filter((Q(department=role.department) | Q(role=role))
                                     | Q(statistic_type__in=stat_types) & Q(**visibility_level))

    result = []

    for stat in stats:
        if not (stat.visibility == VisibilityType.EMPLOYEES and not user.role.
                observing_statistics.select_related('statistic').only('statistic').filter(statistic=stat)):

            user_stats = UserStatistic.objects \
                .filter(role=role, statistic=stat, day__range=[data['monday'], data['sunday']]) \
                .order_by('day')

            result.append(StatsForUserSerializer({'statistic': stat, 'user_statistics': user_stats}).data)
    return result
