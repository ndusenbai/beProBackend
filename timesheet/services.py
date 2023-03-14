from calendar import monthrange
from datetime import date, timedelta, datetime
from typing import OrderedDict

import geopy.distance
import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.db.transaction import atomic
from django.utils import timezone

from bepro_statistics.models import Statistic, UserStatistic
from companies.models import Role, Department, CompanyService
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
        .order_by('day').select_related('role', 'role__department')


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
                    text = 'Created automatically within get_timesheet_by_month()'
                    result.append(create_day_off_timesheet(role_id, date_formatted, text))
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


def create_day_off_timesheet(role_id, date_formatted, text):
    day_off_timesheet = TimeSheet.objects.create(
        role_id=role_id,
        day=date_formatted,
        check_in=None,
        check_out=None,
        time_from=None,
        time_to=None,
        debug_comment=text,
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


def create_future_day_timesheet(role_id, date_formatted, time_from, time_to, text):
    future_day_timesheet = TimeSheet.objects.create(
        role_id=role_id,
        day=date_formatted,
        check_in=None,
        check_out=None,
        time_from=time_from,
        time_to=time_to,
        debug_comment=text,
        status=TimeSheetChoices.FUTURE_DAY,
    )
    return {
        'id': future_day_timesheet.id,
        'role': role_id,
        'day': date_formatted,
        'check_in': '',
        'check_out': '',
        'time_from': time_from,
        'time_to': time_to,
        'comment': '',
        'file': None,
        'status': TimeSheetChoices.FUTURE_DAY,
        'status_decoded': TimeSheetChoices.get_status(TimeSheetChoices.FUTURE_DAY),
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
    today = timezone.now().date()
    last_timesheet = TimeSheet.objects.filter(
            role=role,
            day__lte=today,
            status__in=[TimeSheetChoices.ON_TIME, TimeSheetChoices.LATE])\
        .order_by('-day').first()

    # TODO: delete if not needed
    # if last_timesheet.status not in [TimeSheetChoices.ON_TIME, TimeSheetChoices.LATE]:
    #     last_timesheet_before = TimeSheet.objects.filter(
    #             role=role,
    #             day__lte=date.today(),
    #             status__in=[TimeSheetChoices.ON_TIME, TimeSheetChoices.LATE])\
    #         .order_by('-day').first()
    #     if last_timesheet_before and last_timesheet_before.check_out is None:
    #         return 'check_in'
    #     return 'check_out'

    if last_timesheet and last_timesheet.check_in and last_timesheet.check_out is None:
        return 'check_in'
    return 'check_out'


def subtract_scores(role, check_in):
    time_sheet = TimeSheet.objects.filter(role=role, day=check_in.date())
    if not time_sheet.exists() or not time_sheet.last().status == TimeSheetChoices.ABSENT:
        reason = role.company.reasons.get(is_auto=True)
        Score.objects.create(role=role, name=reason.name, points=reason.score, created_at=check_in)


def check_distance(role: Role, latitude: float, longitude: float) -> None:
    zones = role.zones.all()
    department = role.department
    all_zones_far = True
    for zone in zones:
        distance = geopy.distance.geodesic((latitude, longitude), (zone.latitude, zone.longitude)).m
        if distance <= zone.radius:
            all_zones_far = False
            break
    distance = geopy.distance.geodesic((latitude, longitude), (department.latitude, department.longitude)).m
    if distance <= department.radius:
        all_zones_far = False
    if all_zones_far:
        raise EmployeeTooFarFromDepartment()



def handle_check_in_timesheet(role: Role, data: dict) -> None:
    last_timesheet = TimeSheet.objects.filter(role=role, day__lte=date.today()).order_by('-day').first()
    if last_timesheet:
        if last_timesheet.check_in and not last_timesheet.check_out:
            raise CheckInAlreadyExistsException()

    check_in = datetime.now(pytz.timezone(settings.TIME_ZONE))

    # getting employee schedule and department timezone
    today_schedule = EmployeeSchedule.objects.get(role=role, week_day=check_in.weekday())
    time_zone = today_schedule.role.department.timezone

    status = TimeSheetChoices.ON_TIME

    # creating datetime schedule with timezone
    time_schedule_datetime = datetime.combine(check_in.date(), today_schedule.time_from)
    time_schedule_datetime = datetime.strptime(f'{time_schedule_datetime.strftime("%Y-%m-%d %H:%M")} {time_zone}',
                                               '%Y-%m-%d %H:%M %z')
    time_schedule_datetime = time_schedule_datetime.astimezone(pytz.timezone(settings.TIME_ZONE))

    # add timedelta for 1 minute late
    time_schedule_end = time_schedule_datetime + timedelta(minutes=1)

    if check_in > time_schedule_end:
        status = TimeSheetChoices.LATE
        subtract_scores(role, check_in)

    # changed logic of creation, because there might be created future_day timesheet

    timesheet, _ = TimeSheet.objects.get_or_create(role=role, day=check_in.date())

    timesheet.check_in = check_in.time()
    timesheet.check_out = None
    timesheet.time_from = today_schedule.time_from
    timesheet.time_to = today_schedule.time_to
    timesheet.status = status
    timesheet.comment = data.get('comment', '')
    timesheet.file = data.get('file', None)
    timesheet.save()

    # TimeSheet.objects.create(
    #     role=role,
    #     day=check_in.date(),
    #     check_in=check_in.time(),
    #     check_out=None,
    #     time_from=today_schedule.time_from,
    #     time_to=today_schedule.time_to,
    #     status=status,
    #     comment=data.get('comment', ''),
    #     file=data.get('file', None),
    # )


@atomic
def create_check_in_timesheet(role: Role, data: dict) -> None:
    if role.in_zone:
        check_distance(role, data['latitude'], data['longitude'])
    handle_check_in_timesheet(role, data)


def get_schedule(role, now_date):
    today_in_employee_schedule = role.employee_schedules.filter(week_day=now_date.weekday())

    if today_in_employee_schedule.exists():
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


def handle_check_out_absent_days(role: Role, data: dict, analytics_enabled: bool) -> bool:
    last_timesheet = TimeSheet.objects.filter(
        role=role,
        day__lte=date.today(),
        status__in=[TimeSheetChoices.ON_TIME, TimeSheetChoices.LATE]).order_by('-day').first()

    today = data['check_out'].date()
    # TODO: delete log messages after testing
    log_message(f'handle_check_out_absent_days. role_id: {role.id}')
    log_message(f"data.check_out: {data['check_out']}")
    log_message(f"today: {today}")
    log_message(f"last_timesheet.day: {last_timesheet.day}")
    log_message(f"date.today: {date.today()}")
    if last_timesheet.day != today:
        if last_timesheet.check_in and not last_timesheet.check_out:
            if analytics_enabled:
                check_statistics(role, last_timesheet.day)
            last_timesheet.check_out = '23:59'
            last_timesheet.debug_comment = 'Automatically filled check_in within create_check_out_timesheet()'
            last_timesheet.save()

        first_absent_day = last_timesheet.day + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        absent_days_qty = (yesterday - first_absent_day).days
        time_sheets = []
        for i in range(absent_days_qty + 1):
            if not TimeSheet.objects.filter(role=role, day=first_absent_day + timedelta(days=i)).exists():
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
    if role.in_zone:
        check_distance(role, data['latitude'], data['longitude'])

    analytics_enabled = CompanyService.objects.get(company=role.user.selected_company).analytics_enabled
    if not handle_check_out_absent_days(role, data, analytics_enabled):
        return False
    if analytics_enabled:
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


def create_future_time_sheet(role_id, day, month, year, status, time_from=None, time_to=None):
    _date = date(year, month, day)
    date_formatted = _date.strftime('%Y-%m-%d')
    text = 'Created automatically within create_future_time_sheet()'
    with atomic():
        if status == 5:
            return create_day_off_timesheet(role_id, date_formatted, text), 201
        elif status == 6:
            # schedules = EmployeeSchedule.objects.filter(role_id=role_id)
            # is_workday_schedule = get_schedule_for_weekday(schedules, _date.weekday())
            # if is_workday_schedule:
            #     local_time_from = is_workday_schedule.time_from
            #     local_time_to = is_workday_schedule.time_to
            # else:
            if not (time_from and time_to):
                return {'message': 'Enter time_from & time_to'}, 400

            local_time_from = time_from
            local_time_to = time_to

            return create_future_day_timesheet(role_id, date_formatted, local_time_from, local_time_to, text), 201
        else:
            return {'message': 'Wrong status!'}, 400


def generate_total_hours(role_id, year, month):
    timesheets = TimeSheet.objects.filter(
        role_id=role_id,
        created_at__year=year,
        created_at__month=month
    )

    # calculate the total working hours
    total_working_hours = timesheets.aggregate(
        total=Sum('check_out') - Sum('check_in')
    )['total']

    return total_working_hours.total_seconds() / 3600.0
