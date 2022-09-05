from celery import shared_task
from datetime import date, datetime

from companies.models import Role
from timesheet.models import TimeSheetChoices, TimeSheet, EmployeeSchedule
from utils.tools import log_message, log_exception


def create_absent_timesheet(role, now_date, schedule: EmployeeSchedule):

    TimeSheet.objects.create(role=role,
                             day=now_date,
                             time_from=schedule.time_from,
                             time_to=schedule.time_to,
                             status=TimeSheetChoices.ABSENT,
                             debug_comment='Created automatically within absence_check task')


def absence_check_request(request):
    absence_check()


@shared_task()
def absence_check():
    now_date = date.today()
    now_time = datetime.now().time()
    log_message(f'started absence_check at {now_date} {now_time}')

    roles = Role.objects.prefetch_related('timesheet', 'employee_schedules', 'department').all()

    for role in roles:
        try:
            if not role.timesheet.filter(day__year=now_date.year,
                                         day__month=now_date.month,
                                         day__day=now_date.day):

                today_in_employee_schedule = role.employee_schedules.filter(week_day=now_date.weekday())
                if today_in_employee_schedule:
                    create_absent_timesheet(role, now_date, today_in_employee_schedule.first())
        except Exception as e:
            log_exception(e, 'error in celery beat absence_check')
