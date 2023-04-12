import django
import os
import pytz


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

<<<<<<< HEAD
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
=======
import datetime
from timesheet.models import TimeSheet, EmployeeSchedule
from companies.models import Department
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from notifications.models import EmployeeNotification


# Loop through each department and send a notification to employees with check-out schedules
for department in Department.objects.all():
    # Convert the time zone string to a pytz timezone object
    timezone_str = department.timezone
    timezone = datetime.timezone(datetime.timedelta(hours=int(timezone_str[:3]), minutes=int(timezone_str[4:])))

    # Convert the current UTC time to the local time zone for the department
    now_local = datetime.datetime.now(timezone)

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
        employee_notification = EmployeeNotification.objects.filter(
            role=schedule.role,
            created_at__date=datetime.date.today(),
            check_out_notified=True
        )

        if not time_sheet.exists() and not employee_notification.exists():
            devices = FCMDevice.objects.filter(user_id=schedule.role.user.id)
            emp_notification, _ = EmployeeNotification.objects.get_or_create(
                role=schedule.role,
                created_at__date=datetime.date.today(),
            )

            emp_notification.check_out_notified = True
            emp_notification.save()

            title = "Don't forget to check out!"
            text = f"Hey {schedule.role.user.full_name}, just a heads up that your shift is coming to an end and you have 5 minutes left to check out. Thanks for all your hard work today!"

            devices.send_message(Message(notification=Notification(title=title, body=text)))
>>>>>>> 9ebc73e8274e868e870930f33438b487a0289996
