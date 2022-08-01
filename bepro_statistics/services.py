import random
import matplotlib.pyplot as plt
from typing import OrderedDict
from datetime import datetime, date, timedelta

from django.apps import apps
from django.conf import settings
from django.db.transaction import atomic
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from auth_user.services import get_user_role
from bepro_statistics.models import StatisticObserver, Statistic, UserStatistic, VisibilityType, StatisticType
from bepro_statistics.serializers import UserStatsSerializer, StatsForUserSerializer
from companies.models import Role, RoleChoices
from timesheet.models import TimeSheet

User = get_user_model()


def get_statistics_queryset(request):
    return apps.get_model(
        app_label='bepro_statistics',
        model_name='Statistic'
    ).objects.filter(Q(department__company=request.user.selected_company) |
                     Q(role__company=request.user.selected_company)).order_by()


@atomic
def create_statistic(serializer):
    employees_list = serializer.validated_data.pop('employees') if 'employees' in serializer.validated_data else None
    statistic = Statistic.objects.create(**serializer.validated_data)
    if employees_list:
        statistic_observers = [
            StatisticObserver(statistic=statistic, role=employee) for employee in employees_list
        ]
        StatisticObserver.objects.bulk_create(statistic_observers)
    return statistic


@atomic
def create_user_statistic(role: Role, data: OrderedDict):
    last_check_in = TimeSheet.objects.filter(role=role, check_out__isnull=True).order_by('-day').first()
    UserStatistic.objects.create(
        role=role,
        statistic_id=data['statistic_id'],
        day=last_check_in.day,
        fact=data['fact'])


@atomic
def bulk_create_observers(data: dict, instance: Statistic):
    employees = data.get('employees')

    if instance.observers.all() and data.get('visibility') != VisibilityType.EMPLOYEES:
        instance.observers.all().delete()

    if employees and data.get('visibility') == VisibilityType.EMPLOYEES:
        instance.observers.all().delete()
        observers = [StatisticObserver(role_id=employee_id, statistic=instance) for employee_id in employees]
        StatisticObserver.objects.bulk_create(observers)
        return data, 200
    elif employees and data.get('visibility') != VisibilityType.EMPLOYEES:
        return {'message': 'Change visibility to Employees'}, 400
    elif not employees and data.get('visibility') == VisibilityType.EMPLOYEES:
        return {'message': 'Input employees'}, 400
    elif not employees and data.get('visibility') != VisibilityType.EMPLOYEES:
        return data, 200


def check_user_permission(user, role):

    if get_user_role(user) == 'superuser':
        return {"visibility__in": {VisibilityType.HIDDEN,
                                   VisibilityType.EMPLOYEES,
                                   VisibilityType.OPEN_DEPARTMENT,
                                   VisibilityType.OPEN_EVERYONE}}

    if hasattr(user, 'role'):
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

    elif not hasattr(user, 'role') and get_user_role(user) == 'owner':
        return {"visibility__in": {VisibilityType.HIDDEN,
                                   VisibilityType.EMPLOYEES,
                                   VisibilityType.OPEN_DEPARTMENT,
                                   VisibilityType.OPEN_EVERYONE}}


def change_user_statistic(data: OrderedDict):
    UserStatistic.objects.update_or_create(
        role=data['role'],
        statistic=data['statistic'],
        day=data['date'],
        defaults={'fact': data['fact']})


def get_stats_for_user(request):

    role = Role.objects.get(id=request.query_params['role_id'])
    now = datetime.now()
    monday = date.today() - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    data = []

    visibility_level = check_user_permission(request.user, role)

    stats = Statistic.objects.filter((Q(department=role.department) | Q(role=role)) & Q(**visibility_level))
    for stat in stats:
        allowed = is_user_allowed_to_stat(request.user, stat)
        if allowed:
            user_stats = UserStatistic.objects \
                .filter(role=role, statistic=stat, day__range=[monday, sunday]) \
                .order_by('day')

            data.append(StatsForUserSerializer({'statistic': stat, 'user_statistics': user_stats}).data)

    return data


def is_user_allowed_to_stat(user: User, stat: Statistic) -> bool:
    is_allowed = False
    try:
        is_allowed = not (stat.visibility == VisibilityType.EMPLOYEES and not user.role.
                          observing_statistics.select_related('statistic').only('statistic').filter(statistic=stat))
    except Role.DoesNotExist:
        if get_user_role(user) == 'superuser':
            is_allowed = True
    return is_allowed


def get_history_stats_for_user(user, data: OrderedDict):

    role = Role.objects.get(id=data['role_id'])
    stat_types = data['statistic_types']
    visibility_level = check_user_permission(user, role)
    stats = Statistic.objects.filter((Q(department=role.department) | Q(role=role))
                                     & Q(statistic_type__in=stat_types) & Q(**visibility_level))

    result = []

    for stat in stats:
        if not (stat.visibility == VisibilityType.EMPLOYEES and not user.role.
                observing_statistics.select_related('statistic').only('statistic').filter(statistic=stat)):

            user_stats = UserStatistic.objects \
                .filter(role=role, statistic=stat, day__range=[data['monday'], data['sunday']]) \
                .order_by('day')

            result.append(StatsForUserSerializer({'statistic': stat, 'user_statistics': user_stats}).data)
    return result


def generate_stat_pdf(role_id: int, statistic_id: int) -> str:
    role = Role.objects.get(id=role_id)
    first_day_of_week = date.today() - timedelta(days=date.today().weekday())
    last_day_of_week = first_day_of_week + timedelta(days=6)

    statistic = Statistic.objects.get(
        (Q(department=role.department) | Q(role=role)),
        id=statistic_id)

    user_stat = UserStatistic.objects.filter(
        statistic=statistic,
        role=role,
        day__range=[first_day_of_week, last_day_of_week],
    ).select_related('statistic').order_by('day')

    user_stat_data = UserStatsSerializer(user_stat, many=True).data
    user_stat_data_dict = {i['day_num']: i for i in user_stat_data}

    if statistic.statistic_type == StatisticType.GENERAL:
        return generate_general_graph_pdf(user_stat_data_dict, statistic)
    elif statistic.statistic_type == StatisticType.INVERTED:
        return generate_inverted_graph_pdf(user_stat_data_dict, statistic)
    elif statistic.statistic_type == StatisticType.DOUBLE:
        return generate_double_graph_pdf(user_stat_data_dict, statistic)

    return 'no_link'


def generate_general_graph_pdf(user_stat_data_dict: dict, statistic: Statistic) -> str:
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = []
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'])
        else:
            y_axis_values.append(0)

    _, ax = plt.subplots()
    plt.plot(days, y_axis_values, marker=".", markersize=14)
    plt.ylabel(statistic.name)
    plt.title('Обычная статистика')
    ax.grid()
    for a, b in zip(days, y_axis_values):
        plt.text(a, b, str(b))
    file_name = save_stat_to_pdf('general_stat')
    plt.show()
    return file_name


def generate_inverted_graph_pdf(user_stat_data_dict: dict, statistic: Statistic) -> str:
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = []
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'] * -1)
        else:
            y_axis_values.append(0)

    _, ax = plt.subplots()
    plt.plot(days, y_axis_values, marker=".", markersize=14)
    plt.ylabel(statistic.name)
    ax.set_yticklabels([item*-1 for item in ax.get_yticks()])
    plt.title('Перевернутая статистика')
    ax.grid()
    for a, b in zip(days, y_axis_values):
        plt.text(a, b, str(b))

    file_name = save_stat_to_pdf('inverted_stat')
    plt.show()
    return file_name


def generate_double_graph_pdf(user_stat_data_dict: dict, statistic: Statistic) -> str:
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = []
    plans = [statistic.plan for i in range(7)]
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'])
        else:
            y_axis_values.append(0)

    _, ax = plt.subplots()
    plt.plot(days, plans, 'r', label='план', marker=".", markersize=14)
    plt.plot(days, y_axis_values, 'C0', label='факт', marker=".", markersize=14)
    plt.ylabel(statistic.name)
    plt.title('Двойная статистика')
    ax.grid()
    plt.legend(loc='best')
    for a, b in zip(days, y_axis_values):
        ax.text(a, b, str(b))
    file_name = save_stat_to_pdf('double_stat')
    plt.show()
    return file_name


def save_stat_to_pdf(statistic_type: str) -> str:
    unique_name = timezone.now().strftime("%y-%m-%d-%H-%M-%S") + '-' + str(random.randint(100, 999))

    match statistic_type:
        case 'general_stat':
            file_name = f'media/statistics/general_stats/{unique_name}.pdf'
        case 'inverted_stat':
            file_name = f'media/statistics/inverted_stats/{unique_name}.pdf'
        case 'double_stat':
            file_name = f'media/statistics/double_stats/{unique_name}.pdf'
        case 'history_stat':
            file_name = f'media/statistics/history_stats/{unique_name}.pdf'

    plt.savefig(file_name)
    return f'{settings.CURRENT_SITE}/{file_name}'


def generate_history_stat_pdf(role: Role, monday: date, sunday: date) -> str:
    statistics = Statistic.objects.filter(Q(department=role.department) | Q(role=role))

    fig, axs = plt.subplots(statistics.count())
    j = 0
    for statistic in statistics:
        user_stat = UserStatistic.objects.filter(
            statistic=statistic,
            role=role,
            day__range=[monday, sunday],
        ).select_related('statistic').order_by('day')
        user_stat_data = UserStatsSerializer(user_stat, many=True).data
        user_stat_data_dict = {i['day_num']: i for i in user_stat_data}

        if statistic.statistic_type == StatisticType.GENERAL:
            generate_general_history_graph_pdf(user_stat_data_dict, axs[j], statistic)
        elif statistic.statistic_type == StatisticType.INVERTED:
            generate_inverted_history_graph_pdf(user_stat_data_dict, axs[j], statistic)
        elif statistic.statistic_type == StatisticType.DOUBLE:
            generate_double_history_graph_pdf(user_stat_data_dict, axs[j], statistic)

        j += 1

    fig.tight_layout()
    fig.set_size_inches(10, 20)
    file_name = save_stat_to_pdf('history_stat')
    plt.show()
    return file_name


def generate_general_history_graph_pdf(user_stat_data_dict, ax, statistic):
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = []
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'])
        else:
            y_axis_values.append(0)

    ax.plot(days, y_axis_values, marker=".", markersize=14)
    ax.set_ylabel(statistic.name)
    ax.set_title('Обычная статистика', pad=20)
    ax.grid()

    for a, b in zip(days, y_axis_values):
        ax.text(a, b, str(b))


def generate_inverted_history_graph_pdf(user_stat_data_dict, ax, statistic):
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = []
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'] * -1)
        else:
            y_axis_values.append(0)

    ax.plot(days, y_axis_values, marker=".", markersize=14)
    ax.set_ylabel(statistic.name)
    # ax.set_yticklabels([item*-1 for item in ax.get_yticks()]) # плывет верстка если взять положительные числа
    ax.set_title('Перевернутая статистика', pad=20)
    ax.grid()

    for a, b in zip(days, y_axis_values):
        ax.text(a, b, str(b))


def generate_double_history_graph_pdf(user_stat_data_dict, ax, statistic):
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = []
    plans = [statistic.plan for i in range(7)]
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'])
        else:
            y_axis_values.append(0)

    ax.plot(days, plans, 'r', label='план', marker=".", markersize=14)
    ax.plot(days, y_axis_values, 'C0', label='факт', marker=".", markersize=14)
    ax.set_ylabel(statistic.name)
    ax.set_title('Двойная статистика', pad=20)
    ax.grid()
    ax.legend(loc='best')

    for a, b in zip(days, y_axis_values):
        ax.text(a, b, str(b))
