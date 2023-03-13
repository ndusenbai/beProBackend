import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import datetime
from django.utils import timezone
from timesheet.models import TimeSheet, EmployeeSchedule
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice

# Get the current time
now = timezone.now()


check_out_schedules = EmployeeSchedule.objects.filter(
    weekday=now.weekday(),
    time_to__gte=now.time(),
    time_to__lte=(now + datetime.timedelta(minutes=5)).time()
)

# Loop through each check-out schedule and send a notification to the employee
for schedule in check_out_schedules:
    time_sheet = TimeSheet.objects.filter(role=schedule.role, day=datetime.date.today())

    if not time_sheet.exists():
        devices = FCMDevice.objects.filter(user_id=schedule.role.user.id)

        title = "Don't forget to check out!"
        text = f"Hey {schedule.role.user.full_name}, just a heads up that your shift is coming to an end and you have 5 minutes left to check out. Thanks for all your hard work today!"

        devices.send_message(Message(notification=Notification(title=title, body=text)))
