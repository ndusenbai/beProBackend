from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from django.db.models import Q
import geopy.distance

from bepro_statistics.models import Statistic, UserStatistic
from companies.models import Role, Department
from timesheet.models import EmployeeSchedule, TimeSheet, TimeSheetChoices
from timesheet.utils import EmployeeTooFarFromDepartment, FillUserStatistic

User = get_user_model()


def get_timesheet_qs_by_month(data: dict) -> TimeSheet:
    first_date_of_month = date(data['year'], data['month'], 1)
    last_date_of_month = date(data['year'], data['month'] + 1, 1) - timedelta(days=1)

    return TimeSheet.objects.filter(
            role_id=data['role_id'],
            day__range=[first_date_of_month, last_date_of_month])\
        .order_by('-day')


def update_timesheet(instance: TimeSheet, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def get_last_timesheet_action(role: Role) -> str:
    last_timesheet = TimeSheet.objects.filter(role=role).order_by('-day').first()

    if last_timesheet and last_timesheet.check_out is None:
        return 'check_in'
    return 'check_out'


def check_distance(department: Department, latitude: float, longitude: float) -> None:
    distance = geopy.distance.geodesic((latitude, longitude), (department.latitude, department.longitude)).m
    if distance > department.radius:
        raise EmployeeTooFarFromDepartment()


def handle_check_in_timesheet(role: Role, data: dict) -> None:
    check_in = data['check_in']
    today_schedule = EmployeeSchedule.objects.get(role=role, week_day=check_in.weekday())

    status = TimeSheetChoices.ON_TIME
    if check_in.time() > today_schedule.time_from:
        status = TimeSheetChoices.LATE

    last_timesheet = TimeSheet.objects.filter(role=role).order_by('-day').first()

    if last_timesheet and last_timesheet.check_out is None:
        last_timesheet.check_out = '23:59'
        last_timesheet.save()

    TimeSheet.objects.create(
        role=role,
        day=check_in.date(),
        check_in=check_in.time(),
        check_out=None,
        time_from=today_schedule.time_from,
        time_to=today_schedule.time_to,
        status=status,
        comment=data.get('comment', ''),
        file=data.get('file', None),
    )


@atomic
def create_check_in_timesheet(role: Role, data: dict) -> None:
    check_distance(role.department, data['latitude'], data['longitude'])
    handle_check_in_timesheet(role, data)


def handle_check_out_timesheet(role: Role, data: dict) -> bool:
    check_out = data['check_out']
    last_timesheet = TimeSheet.objects.filter(role=role).order_by('-day').first()

    if last_timesheet.day != date.today():
        if not last_timesheet.check_out:
            last_timesheet.check_out = '23:59'
            last_timesheet.save()

        first_absent_day = last_timesheet.day + timedelta(days=1)
        yesterday = date.today() - timedelta(days=1)
        absent_days_qty = (yesterday - first_absent_day).days
        time_sheets = []
        for i in range(absent_days_qty + 1):
            time_sheets.append(
                TimeSheet(
                    role=role,
                    day=first_absent_day + timedelta(days=i),
                    check_in=None,
                    check_out=None,
                    time_from='00:00',
                    time_to='23:59',
                    comment='Automatically filled',
                    file=None,
                    status=TimeSheetChoices.ABSENT,
                )
            )
        TimeSheet.objects.bulk_create(time_sheets)
        return False

    last_timesheet.check_out = check_out
    last_timesheet.save()
    return True


def check_statistics(role: Role, check_out_date) -> None:
    department = role.department
    stats = Statistic.objects.filter(Q(department=department) | Q(role=role))

    for stat in stats:
        if not UserStatistic.objects.filter(role=role, statistic=stat, day=check_out_date.date()).exists():
            raise FillUserStatistic()


@atomic
def create_check_out_timesheet(role: Role, data: dict) -> bool:
    check_distance(role.department, data['latitude'], data['longitude'])
    check_statistics(role, data['check_out'])
    return handle_check_out_timesheet(role, data)
