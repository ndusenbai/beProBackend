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
from notifications.models import EmployeeNotification


# Loop through each department and send a notification to employees with check-in schedules
for department in Department.objects.all():
    # Convert the time zone string to a pytz timezone object
    timezone_str = department.timezone
    timezone = datetime.timezone(datetime.timedelta(hours=int(timezone_str[:3]), minutes=int(timezone_str[4:])))

    # Convert the current UTC time to the local time zone for the department
    now_local = datetime.datetime.now(timezone)

    # Get all employee schedules for the department that have a check-in time within the next 5 minutes
    check_in_schedules = EmployeeSchedule.objects.filter(
        role__department=department,
        week_day=now_local.weekday(),
        time_from__gte=now_local.time(),
        time_from__lte=(now_local + datetime.timedelta(minutes=5)).time()
    )

    # Loop through each check-in schedule and send a notification to the employee
    for schedule in check_in_schedules:
        time_sheet = TimeSheet.objects.filter(role=schedule.role, day=datetime.date.today(), check_in_new__isnull=False)
        employee_notification = EmployeeNotification.objects.filter(
            role=schedule.role,
            created_at__date=datetime.date.today(),
            check_in_notified=True
        )

        if not time_sheet.exists() and not employee_notification.exists():
            devices = FCMDevice.objects.filter(user_id=schedule.role.user.id)
            emp_notification, _ = EmployeeNotification.objects.get_or_create(
                role=schedule.role,
                created_at__date=datetime.date.today(),
            )
            emp_notification.check_in_notified = True
            emp_notification.save()
            title = "Don't forget to check in!"
            text = f"Hey {schedule.role.user.full_name}, just a quick reminder that your shift is starting soon and you have 5 minutes left to check in. See you soon!"

            devices.send_message(Message(notification=Notification(title=title, body=text)))
