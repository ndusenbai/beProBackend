import datetime
from django.utils import timezone
from timesheet.models import EmployeeSchedule, TimeSheet
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice

# Get the current time
now = timezone.now()

# Get all employee schedules that have a check-in time within the next 5 minutes
check_in_schedules = EmployeeSchedule.objects.filter(
    weekday=now.weekday(),
    time_from__gte=now.time(),
    time_from__lte=(now + datetime.timedelta(minutes=5)).time()
)

for schedule in check_in_schedules:
    time_sheet = TimeSheet.objects.filter(role=schedule.role, day=datetime.date.today())

    if not time_sheet.exists():
        devices = FCMDevice.objects.filter(user_id=schedule.role.user.id)

        title = "Don't forget to check in!"
        text = f"Hey {schedule.role.user.full_name}, just a quick reminder that your shift is starting soon and you have 5 minutes left to check in. See you soon!"

        devices.send_message(Message(notification=Notification(title=title, body=text)))
