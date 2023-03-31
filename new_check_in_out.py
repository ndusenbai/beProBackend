import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from datetime import datetime
from django.apps import apps


TimeSheet = apps.get_model('timesheet', 'TimeSheet')
for timesheet in TimeSheet.objects.all():
    if timesheet.check_in:
        timesheet.check_in_new = datetime.combine(timesheet.day, timesheet.check_in)
    if timesheet.check_out:
        timesheet.check_out_new = datetime.combine(timesheet.day, timesheet.check_out)
    timesheet.save()


