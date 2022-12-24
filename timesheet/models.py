from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from companies.models import Department, Company
from utils.models import BaseModel

User = get_user_model()


class TimeSheetChoices(models.IntegerChoices):
    ON_TIME = 1, 'On time'
    LATE = 2, 'Late'
    ABSENT = 3, 'Absent'
    ON_VACATION = 4, 'On vacation'
    DAY_OFF = 5, 'Day off'
    FUTURE_DAY = 6, 'Future day'

    @staticmethod
    def get_status(status):
        if status == TimeSheetChoices.ON_TIME:
            return 'on_time'
        elif status == TimeSheetChoices.LATE:
            return 'late'
        elif status == TimeSheetChoices.ABSENT:
            return 'absent'
        elif status == TimeSheetChoices.ON_VACATION:
            return 'on_vacation'
        elif status == TimeSheetChoices.DAY_OFF:
            return 'day_off'
        elif status == TimeSheetChoices.FUTURE_DAY:
            return 'future_day'
        return ''


class TimeSheet(BaseModel):
    role = models.ForeignKey(to='companies.Role', on_delete=models.CASCADE, related_name='timesheet')
    day = models.DateField()
    check_in = models.TimeField(null=True)
    check_out = models.TimeField(null=True, blank=True)
    time_from = models.TimeField(null=True)
    time_to = models.TimeField(null=True)
    comment = models.TextField(blank=True)
    debug_comment = models.TextField(blank=True)
    file = models.FileField(upload_to='timesheet/', null=True, blank=True,)
    status = models.PositiveSmallIntegerField(choices=TimeSheetChoices.choices, default=TimeSheetChoices.ON_TIME)
    timezone = models.CharField(max_length=10, default='+06:00')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'day'], name='unique timesheet'),
        ]
        ordering = ('day',)

    def __str__(self):
        return f'{self.role} @{self.day}'


class WeekDayChoices(models.IntegerChoices):
    MONDAY = 0, 'Monday'
    TUESDAY = 1, 'Tuesday'
    WEDNESDAY = 2, 'Wednesday'
    THURSDAY = 3, 'Thursday'
    FRIDAY = 4, 'Friday'
    SATURDAY = 5, 'Saturday'
    SUNDAY = 6, 'Sunday'


class DepartmentSchedule(BaseModel):
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE, related_name='department_schedules')
    week_day = models.IntegerField(choices=WeekDayChoices.choices, validators=[MinValueValidator(0), MaxValueValidator(6)])
    time_from = models.TimeField()
    time_to = models.TimeField()

    class Meta:
        unique_together = ('department', 'week_day')

    def __str__(self):
        return f'{self.department} - {self.week_day}'


class EmployeeSchedule(BaseModel):
    role = models.ForeignKey(to='companies.Role', on_delete=models.CASCADE, related_name='employee_schedules')
    week_day = models.IntegerField(choices=WeekDayChoices.choices, validators=[MinValueValidator(0), MaxValueValidator(6)])
    time_from = models.TimeField()
    time_to = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'week_day'], name='unique schedule'),
        ]
        ordering = ('week_day',)

    def __str__(self):
        return f'{self.role} - {WeekDayChoices.choices[self.week_day][1]}'
