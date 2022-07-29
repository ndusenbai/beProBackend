from typing import OrderedDict
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from django.db.models import Q
import geopy.distance

from bepro_statistics.models import Statistic, UserStatistic
from companies.models import Role, Department
from scores.models import Score, Reason
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


def subtract_scores(role, check_in):
    now_date = date.today()
    time_sheet = TimeSheet.objects.filter(role=role, day=now_date)
    if not time_sheet.exists() or not time_sheet.last().status == TimeSheetChoices.ABSENT:
        reason = role.company.reasons.get(is_auto=True)
        Score.objects.create(role=role, name=reason.name, points=reason.score, created_at=check_in)
        return True
    else:
        return False


def check_distance(department: Department, latitude: float, longitude: float) -> None:
    distance = geopy.distance.geodesic((latitude, longitude), (department.latitude, department.longitude)).m
    if distance > department.radius:
        raise EmployeeTooFarFromDepartment()


def handle_check_in_timesheet(role: Role, data: dict) -> None:
    check_in = data['check_in']
    today_schedule = EmployeeSchedule.objects.get(role=role, week_day=check_in.weekday())
    subtraction_result = True
    status = TimeSheetChoices.ON_TIME

    if check_in.time() > today_schedule.time_from:
        status = TimeSheetChoices.LATE
        subtraction_result = subtract_scores(role, check_in)

    last_timesheet = TimeSheet.objects.filter(role=role).order_by('-day').first()

    if last_timesheet and last_timesheet.check_out is None:
        last_timesheet.check_out = '23:59'
        last_timesheet.save()

    if subtraction_result:
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


def get_schedule(role, now_date):
    today_in_employee_schedule = role.employee_schedules.filter(week_day=now_date.weekday())

    if today_in_employee_schedule:
        return today_in_employee_schedule.last()
    else:
        today_in_departament_schedule = role.department.department_schedules.filter(week_day=now_date.weekday())
        return today_in_departament_schedule.last()


@atomic
def set_took_off(role: Role, data: dict):
    now_date = date.today()

    time_sheet = TimeSheet.objects.filter(role=role, day=now_date)
    if time_sheet.exists():
        if time_sheet.last().check_out:
            return {'message': 'Вы уже осуществили check out на текущий день'}, 400

        time_sheet = time_sheet.last()
        time_sheet.check_in = None
        time_sheet.check_out = None
        time_sheet.status = TimeSheetChoices.ABSENT
        time_sheet.save()
    else:
        schedule = get_schedule(role, now_date)
        if schedule:
            TimeSheet.objects.create(role=role, status=TimeSheetChoices.ABSENT, day=now_date,
                                     time_to=schedule.time_to, time_from=schedule.time_from, **data)

    return {'message': 'created'}, 201


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


def bulk_create_vacation_timesheets(data):
    vacation_date = data['start_vacation_date']
    end_vacation_date = data['end_vacation_date']
    role = data['role']
    timesheets = []
    while True:
        if vacation_date != end_vacation_date + timedelta(days=1):
            timesheets.append(TimeSheet(
                role=role,
                day=vacation_date,
                time_from='00:00',
                time_to='23:59',
                status=TimeSheetChoices.ON_VACATION
            ))

            vacation_date = vacation_date + timedelta(days=1)
        else:
            break

    TimeSheet.objects.bulk_create(timesheets)
    return {'message': 'created'}, 201


@atomic
def change_timesheet(timesheet: TimeSheet, data: OrderedDict) -> None:
    new_status = data['status']

    if timesheet.status == TimeSheetChoices.LATE and new_status == TimeSheetChoices.ON_TIME:
        reason = Reason.objects.filter(is_auto=True, company=timesheet.role.company)
        if reason.exists():
            score = reason.first().score
            auto_score = Score.objects.filter(role=timesheet.role, created_at__date=timesheet.day, points=score)
            if auto_score:
                auto_score.delete()

    timesheet.status = new_status
    timesheet.save()


@atomic
def create_vacation(data: OrderedDict):

    if TimeSheet.objects.filter(day=data['start_vacation_date'], role_id=data['role']).exists():
        return {'message': 'У этого сотрудника уже есть статус check_in на указанный промежуток.'}, 400

    if data['start_vacation_date'] >= data['end_vacation_date']:
        return {'message': 'Дата начала отпуска не может быть позже или равным, чем дата окончания отпуска'}, 400

    return bulk_create_vacation_timesheets(data)
