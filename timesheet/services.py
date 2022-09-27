from calendar import monthrange
from datetime import date, timedelta, timezone, datetime
from typing import OrderedDict

import geopy.distance
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.transaction import atomic

from bepro_statistics.models import Statistic, UserStatistic
from companies.models import Role, Department
from scores.models import Score, Reason
from timesheet.models import EmployeeSchedule, TimeSheet, TimeSheetChoices
from timesheet.serializers import TimeSheetModelSerializer
from timesheet.utils import EmployeeTooFarFromDepartment, FillUserStatistic, CheckInAlreadyExistsException
from utils.tools import log_message

User = get_user_model()


def get_timesheet_qs_by_month(role_id, year, month) -> TimeSheet:
    first_date_of_month = date(year, month, 1)
    if month == 12:
        last_date_of_month = date(year, 12, 31)
    else:
        last_date_of_month = date(year, month + 1, 1) - timedelta(days=1)

    return TimeSheet.objects.filter(
            role_id=role_id,
            day__range=[first_date_of_month, last_date_of_month])\
        .order_by('day')


def get_timesheet_for_day(timesheets, day):
    for timesheet in timesheets:
        if timesheet['day'] == day:
            return timesheet
    return None


def get_schedule_for_weekday(schedules, num_day_of_month):
    for schedule in schedules:
        if schedule.week_day == num_day_of_month:
            return schedule
    return None


def get_timesheet_by_month(role_id, year, month):
    qs = get_timesheet_qs_by_month(role_id, year, month)
    timesheets = TimeSheetModelSerializer(qs, many=True).data
    schedules = EmployeeSchedule.objects.filter(role_id=role_id)
    first_weekday, num_days_of_month = monthrange(year, month)
    result = []
    today = date.today()
    for num_day_of_month in range(1, num_days_of_month+1):
        _date = date(year, month, num_day_of_month)
        date_formatted = _date.strftime('%Y-%m-%d')
        if _date < today:
            timesheet_for_day = get_timesheet_for_day(timesheets, date_formatted)
            if timesheet_for_day:
                result.append(timesheet_for_day)
            else:
                is_workday_schedule = get_schedule_for_weekday(schedules, _date.weekday())
                if is_workday_schedule:
                    result.append(create_absent_timesheet(role_id, date_formatted, is_workday_schedule))
                else:
                    result.append(create_day_off_timesheet(role_id, date_formatted))
        else:
            timesheet_for_day = get_timesheet_for_day(timesheets, date_formatted)
            if timesheet_for_day:
                result.append(timesheet_for_day)
            else:
                is_workday_schedule = get_schedule_for_weekday(schedules, _date.weekday())
                if is_workday_schedule:
                    result.append(fake_future_day_timesheet(role_id, date_formatted, is_workday_schedule))
                else:
                    result.append(fake_future_day_off_timesheet(role_id, date_formatted))

    return result


def create_absent_timesheet(role_id, date_formatted, is_workday_schedule):
    absent_timesheet = TimeSheet.objects.create(
        role_id=role_id,
        day=date_formatted,
        check_in=None,
        check_out=None,
        time_from=is_workday_schedule.time_from,
        time_to=is_workday_schedule.time_to,
        debug_comment='Created automatically within get_timesheet_by_month()',
        status=TimeSheetChoices.ABSENT,
    )
    return {
        'id': absent_timesheet.id,
        'role': role_id,
        'day': date_formatted,
        'check_in': '',
        'check_out': '',
        'time_from': is_workday_schedule.time_from,
        'time_to': is_workday_schedule.time_to,
        'comment': '',
        'file': None,
        'status': TimeSheetChoices.ABSENT,
        'status_decoded': TimeSheetChoices.get_status(TimeSheetChoices.ABSENT),
    }


def create_day_off_timesheet(role_id, date_formatted):
    day_off_timesheet = TimeSheet.objects.create(
        role_id=role_id,
        day=date_formatted,
        check_in=None,
        check_out=None,
        time_from=None,
        time_to=None,
        debug_comment='Created automatically within get_timesheet_by_month()',
        status=TimeSheetChoices.DAY_OFF,
    )
    return {
        'id': day_off_timesheet.id,
        'role': role_id,
        'day': date_formatted,
        'check_in': '',
        'check_out': '',
        'time_from': '',
        'time_to': '',
        'comment': '',
        'file': None,
        'status': TimeSheetChoices.DAY_OFF,
        'status_decoded': TimeSheetChoices.get_status(TimeSheetChoices.DAY_OFF),
    }


def fake_future_day_timesheet(role_id, date_formatted, is_workday_schedule):
    return {
        'id': None,
        'role': role_id,
        'day': date_formatted,
        'check_in': '',
        'check_out': '',
        'time_from': is_workday_schedule.time_from,
        'time_to': is_workday_schedule.time_to,
        'comment': '',
        'file': None,
        'status': TimeSheetChoices.FUTURE_DAY,
        'status_decoded': TimeSheetChoices.get_status(TimeSheetChoices.FUTURE_DAY),
    }


def fake_future_day_off_timesheet(role_id, date_formatted):
    return {
        'id': None,
        'role': role_id,
        'day': date_formatted,
        'check_in': '',
        'check_out': '',
        'time_from': '',
        'time_to': '',
        'comment': '',
        'file': None,
        'status': TimeSheetChoices.DAY_OFF,
        'status_decoded': TimeSheetChoices.get_status(TimeSheetChoices.DAY_OFF),
    }


def update_timesheet(instance: TimeSheet, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def get_last_timesheet_action(role: Role) -> str:
    today = datetime.now().date()
    last_timesheet = TimeSheet.objects.filter(role=role, day__lte=today).order_by('-day').first()

    if last_timesheet and last_timesheet.check_out is None:
        return 'check_in'
    return 'check_out'


def subtract_scores(role, check_in):
    time_sheet = TimeSheet.objects.filter(role=role, day=check_in)
    if not time_sheet.exists() or not time_sheet.last().status == TimeSheetChoices.ABSENT:
        reason = role.company.reasons.get(is_auto=True)
        Score.objects.create(role=role, name=reason.name, points=reason.score, created_at=check_in)


def check_distance(department: Department, latitude: float, longitude: float) -> None:
    distance = geopy.distance.geodesic((latitude, longitude), (department.latitude, department.longitude)).m
    if distance > department.radius:
        raise EmployeeTooFarFromDepartment()


def handle_check_in_timesheet(role: Role, data: dict) -> None:
    last_timesheet = TimeSheet.objects.filter(role=role, day__lte=date.today()).order_by('-day').first()

    if last_timesheet.check_in and not last_timesheet.check_out:
        raise CheckInAlreadyExistsException()

    check_in = data['check_in']
    today_schedule = EmployeeSchedule.objects.get(role=role, week_day=check_in.weekday())
    status = TimeSheetChoices.ON_TIME

    if check_in.time() > today_schedule.time_from:
        status = TimeSheetChoices.LATE
        subtract_scores(role, check_in)

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
    schedule = get_schedule(role, now_date)

    if time_sheet.exists():
        time_sheet = time_sheet.last()
        if time_sheet.status == TimeSheetChoices.ON_VACATION:
            return {'message': 'Нельзя отпроситься на время отпуска'}, 400
        if time_sheet.check_out:
            return {'message': 'Вы уже осуществили check out на текущий день'}, 400

        time_sheet.check_in = schedule.time_from
        time_sheet.check_out = schedule.time_to
        time_sheet.status = TimeSheetChoices.ABSENT
        time_sheet.save()
    else:
        if schedule:
            TimeSheet.objects.create(role=role, status=TimeSheetChoices.ABSENT, day=now_date, check_in=schedule.time_from,
                                     check_out=schedule.time_to, time_to=schedule.time_to, time_from=schedule.time_from, **data)

    return {'message': 'created'}, 201


def handle_check_out_timesheet(role: Role, data: dict):
    check_out = data['check_out']
    last_timesheet = TimeSheet.objects.filter(role=role, day__lte=date.today()).order_by('-day').first()
    last_timesheet.check_out = check_out
    last_timesheet.save()


def handle_check_out_absent_days(role: Role, data: dict) -> bool:
    last_timesheet = TimeSheet.objects.filter(role=role, day__lte=date.today()).order_by('-day').first()
    today = data['check_out'].date()
    log_message(f'handle_check_out_absent_days. role_id: {role.id}')
    log_message(f"data.check_out: {data['check_out']}")
    log_message(f"today: {today}")
    log_message(f"last_timesheet.day: {last_timesheet.day}")
    log_message(f"date.today: {date.today()}")
    if last_timesheet.day != today:
        if last_timesheet.check_in and not last_timesheet.check_out and not last_timesheet.debug_comment:
            check_statistics(role, last_timesheet.day)
            last_timesheet.check_out = '23:59'
            last_timesheet.save()

        first_absent_day = last_timesheet.day + timedelta(days=1)
        yesterday = today - timedelta(days=1)
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
                    debug_comment='Created automatically within handle_check_out_absent_days()',
                    file=None,
                    status=TimeSheetChoices.ABSENT,
                )
            )
        TimeSheet.objects.bulk_create(time_sheets)
        return False
    return True


def check_statistics(role: Role, _date: datetime | date) -> None:
    if isinstance(_date, datetime):
        _date = _date.date()

    department = role.department
    stats = Statistic.objects.filter(Q(department=department) | Q(role=role))

    for stat in stats:
        if not UserStatistic.objects.filter(role=role, statistic=stat, day=_date).exists():
            raise FillUserStatistic()


@atomic
def create_check_out_timesheet(role: Role, data: dict) -> bool:
    if not handle_check_out_absent_days(role, data):
        return False
    check_statistics(role, data['check_out'])
    handle_check_out_timesheet(role, data)


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

    if data['start_vacation_date'] > data['end_vacation_date']:
        return {'message': 'Дата начала отпуска не может быть позже или равным, чем дата окончания отпуска'}, 400

    return bulk_create_vacation_timesheets(data)
