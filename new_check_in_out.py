import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from datetime import datetime
from django.apps import apps


def copy_time_fields(apps):
    TimeSheet = apps.get_model('timesheet', 'TimeSheet')
    for timesheet in TimeSheet.objects.all():
        timesheet.check_in = datetime.combine(timesheet.day, timesheet.check_in)
        timesheet.check_out = datetime.combine(timesheet.day, timesheet.check_out)
        timesheet.save()
