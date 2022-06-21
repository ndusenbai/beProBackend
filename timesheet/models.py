from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from companies.models import Department, User, Company
from utils.models import BaseModel

User = get_user_model()


class TimeSheetChoices(models.IntegerChoices):
    ON_TIME = 1, 'On time'
    LATE = 2, 'Late'
    ABSENT = 3, 'Absent'
    ON_VACATION = 4, 'On vacation'


class TimeSheet(BaseModel):
    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, related_name='timesheet')
    company = models.ForeignKey(to='companies.Company', on_delete=models.DO_NOTHING)
    day = models.DateField()
    check_in = models.TimeField(null=True)
    check_out = models.TimeField(null=True, blank=True)
    time_from = models.TimeField()
    time_to = models.TimeField()
    comment = models.TextField(blank=True)
    file = models.FileField(upload_to='timesheet/', null=True, blank=True,)
    status = models.PositiveSmallIntegerField(choices=TimeSheetChoices.choices, default=TimeSheetChoices.ON_TIME)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'company', 'day'], name='unique timesheet in company for user'),
        ]

    def __str__(self):
        return f'{self.user}, {self.company} @{self.day}'


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
    week_day = models.IntegerField(choices=WeekDayChoices.choices, validators=[MinValueValidator(1), MaxValueValidator(7)])
    time_from = models.TimeField()
    time_to = models.TimeField()

    class Meta:
        unique_together = ('department', 'week_day')

    def __str__(self):
        return f'{self.department} - {self.week_day}'


class EmployeeSchedule(BaseModel):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='employee_schedules')
    company = models.ForeignKey(to=Company, on_delete=models.CASCADE, null=True)
    week_day = models.IntegerField(choices=WeekDayChoices.choices, validators=[MinValueValidator(1), MaxValueValidator(7)])
    time_from = models.TimeField()
    time_to = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'company', 'week_day'], name='unique schedule in company for user'),
        ]

    def __str__(self):
        return f'{self.user}@{self.company} - {WeekDayChoices.choices[self.week_day][1]}'
