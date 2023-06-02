import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
import after_response
import datetime
from timesheet.models import TimeSheet, EmployeeSchedule
from companies.models import Department
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from notifications.models import EmployeeNotification
from django.utils.translation import gettext_lazy as _


@after_response.enable
def notify_check_in():
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
                if devices.exists():
                    emp_notification, _ = EmployeeNotification.objects.get_or_create(
                        role=schedule.role,
                        created_at__date=datetime.date.today(),
                    )
                    emp_notification.check_in_notified = True
                    emp_notification.save()

                    title = "Не забудьте сделать check in!"
                    text = f"Привет {schedule.role.user.full_name}, просто напоминаю, что ваша смена скоро начинается, и у вас осталось 5 минут, чтобы сделать check in. До скорой встречи!"

                    if schedule.role.user.language == 'kk':
                        title = "Check in жасауды ұмытпаңыз!"
                        text = f"Сәлем {schedule.role.user.full_name}, сіздің ауысымыңыз жақында басталатынын және check in жасауға 5 минут қалғанын еске саламын. Жақын кездесуге дейін!"

                    devices.send_message(Message(notification=Notification(title=title, body=text)))


@after_response.enable
def notify_check_out():
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
            time_sheet = TimeSheet.objects.filter(role=schedule.role, day=datetime.date.today(), check_in_out__isnull=False)
            employee_notification = EmployeeNotification.objects.filter(
                role=schedule.role,
                created_at__date=datetime.date.today(),
                check_out_notified=True
            )

            if not time_sheet.exists() and not employee_notification.exists():
                devices = FCMDevice.objects.filter(user_id=schedule.role.user.id)
                if devices.exists():
                    emp_notification, _ = EmployeeNotification.objects.get_or_create(
                        role=schedule.role,
                        created_at__date=datetime.date.today(),
                    )

                    emp_notification.check_out_notified = True
                    emp_notification.save()

                    title = "Не забудьте сделать check out!"
                    text = f"Привет {schedule.role.user.full_name}, просто предупреждаю, что ваша смена подходит к концу и у вас осталось 5 минут, чтобы сделать check out. Спасибо за всю вашу сегодняшнюю тяжелую работу!"

                    if schedule.role.user.language == 'kk':
                        title = "Check out жасауды ұмытпаңыз!"
                        text = f"Сәлем {schedule.role.user.full_name}, мен сіздің ауысымыңыз аяқталып жатқанын және check out жасауға 5 минут қалғанын ескертемін. Бүгінгі барлық қажырлы еңбегіңіз үшін рахмет!"

                    devices.send_message(Message(notification=Notification(title=title, body=text)))
