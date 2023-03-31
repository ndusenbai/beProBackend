import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from datetime import datetime
from django.apps import apps


TimeSheet = apps.get_model('timesheet', 'TimeSheet')
for timesheet in TimeSheet.objects.filter(check_in__isnull=False, check_out__isnull=False):
    timesheet.check_in = datetime.combine(timesheet.day, timesheet.check_in)
    timesheet.check_out = datetime.combine(timesheet.day, timesheet.check_out)
    timesheet.save()


