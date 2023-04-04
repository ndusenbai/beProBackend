import django
import os
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from datetime import datetime, time, timedelta
from django.utils import timezone
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from timesheet.models import TimeSheet, EmployeeSchedule, Employee, Department


# Get the current time in UTC
now_utc = timezone.now()

# Get all employee schedules that have a check-out time within the next 5 minutes in their respective time zones
check_out_schedules = EmployeeSchedule.objects.filter(
    week_day=now_utc.weekday(),
    time_to__gte=now_utc.time(),
    time_to__lte=(now_utc + timedelta(minutes=5)).time()
)

for schedule in check_out_schedules:
    # Get the employee's time zone from their department
    employee_time_zone = pytz.timezone(schedule.role.department.time_zone)

    # Convert the current time to the employee's time zone
    now_employee_time_zone = now_utc.astimezone(employee_time_zone)

    # Get the end time of the employee's shift in the employee's time zone
    end_time_employee_time_zone = datetime.combine(now_employee_time_zone.date(), schedule.time_to)

    # Get all devices associated with the employee
    devices = FCMDevice.objects.filter(user_id=schedule.role.user.id)

    # Send a notification if the employee's check-out time is within the next 5 minutes in their time zone
    if (end_time_employee_time_zone - now_employee_time_zone).total_seconds() <= 5*60:
        title = "Don't forget to check out!"
        text = f"Hey {schedule.role.user.full_name}, just a heads up that your shift is coming to an end and you have 5 minutes left to check out. Thanks for all your hard work today!"

        devices.send_message(Message(notification=Notification(title=title, body=text)))
