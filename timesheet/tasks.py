from celery import shared_task
from datetime import date, time
from django.apps import apps
from django.db.models import Q
from timesheet.models import TimeSheetChoices


def create_absent_timesheet(role, now_date):
    now_time = time()

    apps.get_model(
        app_label='timesheet',
        model_name='TimeSheet'
    ).objects.create(role=role,
                     day=now_date,
                     time_from=now_time,
                     time_to=now_time,
                     status=TimeSheetChoices.ABSENT)


@shared_task()
def absence_check():
    now_date = date.today()
    roles = apps.get_model(
                app_label='companies',
                model_name='Role'
            ).objects.all()

    for role in roles:

        for timesheet in role.timesheet.filter(day__year=now_date.year,
                                               day__month=now_date.month,
                                               day__day=now_date.day):

            if not timesheet:

                today_in_employee_schedule = role.employee_schedules.filter(week_day=now_date.weekday())
                if today_in_employee_schedule:
                    create_absent_timesheet(role, now_date)
                else:
                    today_in_departament_schedule = role.department.department_schedules.filter(week_day=now_date.weekday())
                    if today_in_departament_schedule:
                        create_absent_timesheet(role, now_date)

            if not timesheet.status == TimeSheetChoices.ON_VACATION:
                timesheet.status = TimeSheetChoices.ABSENT
                timesheet.save()
