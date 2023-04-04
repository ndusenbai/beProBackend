import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import datetime
from django.utils import timezone
from timesheet.models import TimeSheet, EmployeeSchedule
from companies.models import Department
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
import pytz

# Get the current time in UTC
now_utc = timezone.now()

# Loop through each department and send a notification to employees with check-out schedules
for department in Department.objects.all():
    # Convert the time zone string to a pytz timezone object
    department_tz = pytz.timezone(department.timezone)

    # Convert the current UTC time to the local time zone for the department
    now_local = now_utc.astimezone(department_tz)

    # Get all employee schedules for the department that have a check-out time within the next 5 minutes
    check_out_schedules = EmployeeSchedule.objects.filter(
        role__department=department,
        week_day=now_local.weekday(),
        time_to__gte=now_local.time(),
        time_to__lte=(now_local + datetime.timedelta(minutes=5)).time()
    )

    # Loop through each check-out schedule and send a notification to the employee
    for schedule in check_out_schedules:
        time_sheet = TimeSheet.objects.filter(role=schedule.role, day=datetime.date.today())

        if not time_sheet.exists():
            devices = FCMDevice.objects.filter(user_id=schedule.role.user.id)

            title = "Don't forget to check out!"
            text = f"Hey {schedule.role.user.full_name}, just a heads up that your shift is coming to an end and you have 5 minutes left to check out. Thanks for all your hard work today!"

            devices.send_message(Message(notification=Notification(title=title, body=text)))
