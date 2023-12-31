import random
import matplotlib.pyplot as plt
from typing import OrderedDict
from datetime import datetime, date, timedelta
from django.utils.translation import gettext_lazy as _

from django.apps import apps
from django.conf import settings
from django.db.transaction import atomic
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from auth_user.services import get_user_role
from bepro_statistics.models import StatisticObserver, Statistic, UserStatistic, VisibilityType, StatisticType
from bepro_statistics.serializers import UserStatsSerializer, StatsForUserSerializer, DynamicUserStatsSerializer
from companies.models import Role, CompanyService
from timesheet.models import TimeSheet, TimeSheetChoices

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


def get_date_for_statistic(role: User, statistic_id: int):
    time_tracking_enabled = CompanyService.objects.get(company=role.user.selected_company).time_tracking_enabled

    if time_tracking_enabled:
        statistic = Statistic.objects.get(id=statistic_id)
        if statistic.role == role or statistic.department == role.department:
            last_check_in = TimeSheet.objects.filter(
                role=role,
                check_in__isnull=False,
                check_in_new__isnull=False,
                check_out__isnull=True,
                check_out_new__isnull=True,
                day__lte=date.today()) \
                .order_by('-day').first()

            if not last_check_in:
                raise Exception(_('Вы не осуществляли check in сегодня'))

            return last_check_in.day
        raise Exception(_('У Вас нет доступа к статистике'))

    return timezone.now().date()


@atomic
def create_user_statistic(role: Role, data: OrderedDict):
    time_tracking_enabled = CompanyService.objects.get(company=role.user.selected_company).time_tracking_enabled

    if time_tracking_enabled:
        return create_user_statistic_when_time_tracking_enabled(role, data)
    else:
        return create_user_statistic_when_time_tracking_disabled(role, data)


def create_user_statistic_when_time_tracking_enabled(role: Role, data: OrderedDict):
    try:
        today_timesheet = TimeSheet.objects.get(role=role, day=date.today())
        if today_timesheet.status == TimeSheetChoices.ABSENT:
            return {'message': _('Вы отпросились, нельзя заполнить статистику')}, 400
        if today_timesheet.status == TimeSheetChoices.ON_VACATION:
            return {'message': _('В отпуске нельзя заполнить статистику')}, 400
        if today_timesheet.check_in and today_timesheet.check_out:
            return {'message': _('Чек-ин и чек-аут заполнены. Нельзя заполнить статистику')}, 400
    except TimeSheet.DoesNotExist:
        pass

    last_check_in = TimeSheet.objects.filter(
        role=role,
        check_in__isnull=False,
        check_out__isnull=True,
        day__lte=date.today()) \
        .order_by('-day').first()

    if not last_check_in:
        return {'message': _('Вы не осуществляли check in сегодня'), }, 400

    UserStatistic.objects.create(
        role=role,
        statistic_id=data['statistic_id'],
        day=last_check_in.day,
        fact=data['fact'],
        created_by=role.user,
        updated_by=role.user,
    )

    return {'message': 'created', }, 200


def create_user_statistic_when_time_tracking_disabled(role: Role, data: OrderedDict):
    UserStatistic.objects.create(
        role=role,
        statistic_id=data['statistic_id'],
        day=timezone.now().date(),
        fact=data['fact'],
        created_by=role.user,
        updated_by=role.user,
    )

    return {'message': 'created', }, 200


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
        return {'message': _('Поменяйте видимость на Employees')}, 400
    elif not employees and data.get('visibility') == VisibilityType.EMPLOYEES:
        return {'message': 'Введите employees'}, 400
    elif not employees and data.get('visibility') != VisibilityType.EMPLOYEES:
        return data, 200


def check_user_permission(observer_user: User, role: Role) -> dict:
    observer_user_role = get_user_role(observer_user)
    is_superuser = get_user_role(observer_user) == 'superuser'
    is_owner_or_hr = observer_user.selected_company == role.user.selected_company and observer_user_role in ['owner', 'hr']

    if is_superuser or is_owner_or_hr:
        return {"visibility__in": {VisibilityType.HIDDEN,
                                   VisibilityType.EMPLOYEES,
                                   VisibilityType.OPEN_DEPARTMENT,
                                   VisibilityType.OPEN_EVERYONE}}

    if hasattr(observer_user, 'role'):
        if observer_user.role == role:
            return {"visibility__in": {VisibilityType.HIDDEN,
                                       VisibilityType.EMPLOYEES,
                                       VisibilityType.OPEN_DEPARTMENT,
                                       VisibilityType.OPEN_EVERYONE}}
        elif observer_user.role.department == role.department:
            return {"visibility__in": {VisibilityType.OPEN_DEPARTMENT,
                                       VisibilityType.OPEN_EVERYONE,
                                       VisibilityType.EMPLOYEES}}
        elif observer_user.role.company == role.company:
            return {"visibility__in": {VisibilityType.OPEN_EVERYONE,
                                       VisibilityType.EMPLOYEES}}
        else:
            return {}

    return {}


def change_user_statistic(user: User, data: OrderedDict):
    defaults = {'fact': data['fact'], 'updated_by': user}
    UserStatistic.objects.update_or_create(
        role=data['role'],
        statistic=data['statistic'],
        day=data['date'],
        defaults=defaults)


def get_stats_for_user(request):

    role = Role.objects.get(id=request.query_params['role_id'])
    now = datetime.now()
    monday = date.today() - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    data = []

    visibility_level = check_user_permission(request.user, role)

    stats = Statistic.objects.filter((Q(department=role.department) | Q(role=role)) & Q(**visibility_level))
    for stat in stats:
        allowed = is_user_allowed_to_stat(request.user, stat, role)
        if allowed:
            user_stats = UserStatistic.objects \
                .filter(role=role, statistic=stat, day__range=[monday, sunday]) \
                .order_by('day')
            data.append(StatsForUserSerializer({'statistic': stat, 'user_statistics': user_stats}).data)

    return data


def is_user_allowed_to_stat(observer_user: User, stat: Statistic, role: Role) -> bool:
    is_allowed = False
    try:
        observer_user_role = get_user_role(observer_user)
        if observer_user.role == role:
            return True
        if not stat.visibility == VisibilityType.EMPLOYEES:
            return True

        is_hr = observer_user.selected_company == role.user.selected_company and observer_user_role == 'hr'
        if is_hr:
            return True

        observer_user_in_statistic_observers = observer_user.role.observing_statistics.select_related('statistic').only('statistic').filter(statistic=stat).exists()
        return observer_user_in_statistic_observers
    except Role.DoesNotExist:
        is_superuser = observer_user_role == 'superuser'
        is_owner = observer_user.selected_company == role.user.selected_company and observer_user_role == 'owner'

        if is_superuser or is_owner:
            return True
    return is_allowed


def get_history_stats_for_user(user, data: OrderedDict):

    role = Role.objects.get(id=data['role_id'])
    stat_types = data['statistic_types']
    visibility_level = check_user_permission(user, role)
    stats = Statistic.objects.filter((Q(department=role.department) | Q(role=role))
                                     & Q(statistic_type__in=stat_types) & Q(**visibility_level))

    result = []

    for stat in stats:
        user_role = getattr(user, 'role', None)

        if user_role is None:
            checking_logic = not (stat.visibility == VisibilityType.EMPLOYEES)

        else:
            checking_logic = not (stat.visibility == VisibilityType.EMPLOYEES and not user.role.
                 observing_statistics.select_related('statistic').only('statistic').filter(statistic=stat))

        if checking_logic:

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
    days = ['', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = [0]
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'])
        else:
            y_axis_values.append(0)

    _, ax = plt.subplots()
    plt.plot(days, y_axis_values, marker=".", markersize=14)
    plt.ylabel(statistic.name)
    plt.title('Обычная статистика')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid()

    del days[0]
    del y_axis_values[0]
    for a, b in zip(days, y_axis_values):
        plt.text(a, b, str(b))
    file_name = save_stat_to_pdf('general_stat')
    plt.show()
    return file_name


def generate_inverted_graph_pdf(user_stat_data_dict: dict, statistic: Statistic) -> str:
    days = ['', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = [0]
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
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(left=0)
    ax.grid()

    del days[0]
    del y_axis_values[0]
    for a, b in zip(days, y_axis_values):
        plt.text(a, b, str(b * -1))

    file_name = save_stat_to_pdf('inverted_stat')
    plt.show()
    return file_name


def generate_double_graph_pdf(user_stat_data_dict: dict, statistic: Statistic) -> str:
    days = ['', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = [0]
    plans = [statistic.plan if i != 0 else 0 for i in range(8)]
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
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid()
    plt.legend(loc='best')

    del days[0]
    del y_axis_values[0]
    for a, b in zip(days, y_axis_values):
        ax.text(a, b, str(b))
    ax.text(days[6], plans[6], str(plans[6]))
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
        case 'dynamic_stat':
            file_name = f'media/statistics/dynamic_stats/{unique_name}.pdf'

    plt.savefig(file_name)
    return f'{settings.CURRENT_SITE}/{file_name}'


def generate_history_stat_pdf(role: Role, monday: date, sunday: date) -> str:
    statistics = Statistic.objects.filter(Q(department=role.department) | Q(role=role))

    statistics_count = statistics.count()
    fig, axs = plt.subplots(statistics_count)
    j = 0
    for statistic in statistics:
        user_stat = UserStatistic.objects.filter(
            statistic=statistic,
            role=role,
            day__range=[monday, sunday],
        ).select_related('statistic').order_by('day')
        user_stat_data = UserStatsSerializer(user_stat, many=True).data
        user_stat_data_dict = {i['day_num']: i for i in user_stat_data}

        ax = axs if statistics_count == 1 else axs[j]
        if statistic.statistic_type == StatisticType.GENERAL:
            generate_general_history_graph_pdf(user_stat_data_dict, ax, statistic)
        elif statistic.statistic_type == StatisticType.INVERTED:
            generate_inverted_history_graph_pdf(user_stat_data_dict, ax, statistic)
        elif statistic.statistic_type == StatisticType.DOUBLE:
            generate_double_history_graph_pdf(user_stat_data_dict, ax, statistic)

        j += 1

    fig.set_size_inches(10, j*5)
    file_name = save_stat_to_pdf('history_stat')
    plt.show()
    return file_name


def generate_general_history_graph_pdf(user_stat_data_dict, ax, statistic):
    days = ['', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = [0]
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'])
        else:
            y_axis_values.append(0)

    ax.plot(days, y_axis_values, marker=".", markersize=14)
    ax.set_ylabel(statistic.name)
    ax.set_title('Обычная статистика', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid()

    del days[0]
    del y_axis_values[0]
    for a, b in zip(days, y_axis_values):
        ax.text(a, b, str(b))


def generate_inverted_history_graph_pdf(user_stat_data_dict, ax, statistic):
    days = ['', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = [0]
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'] * -1)
        else:
            y_axis_values.append(0)

    ax.plot(days, y_axis_values, marker=".", markersize=14)
    ax.set_ylabel(statistic.name)
    # ax.set_yticklabels([item*-1 for item in ax.get_yticks()]) # плывет верстка если взять положительные числа
    ax.set_title('Перевернутая статистика', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(left=0)
    ax.grid()

    del days[0]
    del y_axis_values[0]
    for a, b in zip(days, y_axis_values):
        ax.text(a, b, str(b * -1))


def generate_double_history_graph_pdf(user_stat_data_dict, ax, statistic):
    days = ['', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    y_axis_values = [0]
    plans = [statistic.plan if i != 0 else 0 for i in range(8)]
    for i in range(7):
        if i in user_stat_data_dict:
            y_axis_values.append(user_stat_data_dict[i]['fact'])
        else:
            y_axis_values.append(0)

    ax.plot(days, plans, 'r', label='план', marker=".", markersize=14)
    ax.plot(days, y_axis_values, 'C0', label='факт', marker=".", markersize=14)
    ax.set_ylabel(statistic.name)
    ax.set_title('Двойная статистика', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid()
    ax.legend(loc='best')

    del days[0]
    del y_axis_values[0]
    for a, b in zip(days, y_axis_values):
        ax.text(a, b, str(b))
    ax.text(days[6], plans[6], str(plans[6]))


def generate_dynamic_stat_pdf(role: Role, statistic: Statistic, start_date: date, end_date: date) -> str:
    user_stat = UserStatistic.objects.filter(
        statistic=statistic, role=role, day__range=[start_date, end_date]
    ).select_related('statistic').order_by('day')

    user_stats = DynamicUserStatsSerializer(user_stat, many=True).data
    user_stats_by_day = {i['day']: i for i in user_stats}
    dates = [str(start_date + timedelta(days=1) * i) for i in range((end_date - start_date).days)]

    inverted = statistic.statistic_type == StatisticType.INVERTED
    polarity = -1 if inverted else 1

    return _make_dynamic_graph(
        statistic=statistic,
        dates=dates,
        fact_values=[user_stats_by_day.get(day, {'fact': 0})['fact'] * polarity for day in dates],
        inverted=inverted,
        plan_values=([statistic.plan for _ in range(len(dates))]
                     if statistic.statistic_type == StatisticType.DOUBLE else None),
    )


def _make_dynamic_graph(
        statistic: Statistic, dates: list, fact_values: list, inverted: bool, plan_values: list | None
) -> str:
    _, axis = plt.subplots(figsize=_get_figure_size(dates))  # create figure and axis
    plt.ylabel(statistic.name)  # set label
    plt.title(_get_title(statistic))  # set title

    if plan_values:
        # set 'plan_values' line
        plt.plot(dates, plan_values, 'r', label='план', marker=".", markersize=14)
        axis.text(dates[-1], plan_values[-1], str(plan_values[-1]))

    # set 'fact_values' line
    plt.plot(dates, fact_values, label='факт', marker=".", markersize=14)
    for a, b in zip(dates, fact_values):
        plt.text(a, b, str(b))

    _customize_axis(axis, inverted)

    file_name = save_stat_to_pdf('dynamic_stat')
    plt.show()
    return file_name


def _get_figure_size(dates: list) -> tuple[float, float]:
    # Calculate the graph size based on the number of dates
    fig_width = max(12., len(dates) / 2)  # minimum width of 12 inches
    fig_height = max(6., len(dates) / 10)  # minimum height of 6 inches
    return fig_width, fig_height


def _get_title(statistic: Statistic) -> str:
    match statistic.statistic_type:
        case StatisticType.GENERAL:
            return 'Обычная статистика'
        case StatisticType.DOUBLE:
            return 'Двойная статистика'
        case StatisticType.INVERTED:
            return 'Перевернутая статистика'


def _customize_axis(axis, inverted: bool) -> None:
    axis.set_xlim(left=0)
    axis.set_ylim(bottom=0) if not inverted else None
    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)
    axis.grid()
    plt.legend(loc='best')
    plt.xticks(rotation=-90)  # rotate dates on x axis
    plt.gcf().subplots_adjust(bottom=0.2)  # bottom padding
