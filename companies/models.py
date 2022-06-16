from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from utils.models import BaseModel

User = get_user_model()


class CompanyTypes(models.IntegerChoices):
    LLC = 1, 'Limited Liability Company'
    SP = 2, 'Sole Proprietorship'


class Company(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    legal_name = models.CharField(max_length=100, unique=True)
    type = models.IntegerField(choices=CompanyTypes.choices, default=CompanyTypes.LLC)
    years_of_work = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.legal_name


class Department(BaseModel):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(to=Company, on_delete=models.CASCADE, related_name='departments')
    address = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=6, default=0, validators=[MinValueValidator(0)])
    longitude = models.DecimalField(max_digits=22, decimal_places=6, default=0, validators=[MinValueValidator(0)])
    is_hr = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} @{self.company}'


class RoleChoices(models.IntegerChoices):
    OWNER = 1, 'Owner'
    HR = 2, 'HR'
    OBSERVER = 3, 'Observer'
    EMPLOYEE = 4, 'Employee'


class Role(BaseModel):
    company = models.ForeignKey(to=Company, on_delete=models.CASCADE)
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=50, choices=RoleChoices.choices, default=RoleChoices.EMPLOYEE)
    user = models.ForeignKey(to='auth_user.User', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company', 'role', 'user'], name='unique role in company for user'),
            models.UniqueConstraint(fields=['department', 'role', 'user'], name='unique role in department for user')
        ]


class WeekDayChoices(models.IntegerChoices):
    MONDAY = 1, 'Monday'
    TUESDAY = 2, 'Tuesday'
    WEDNESDAY = 3, 'Wednesday'
    THURSDAY = 4, 'Thursday'
    FRIDAY = 5, 'Friday'
    SATURDAY = 6, 'Saturday'
    SUNDAY = 7, 'Sunday'


class DepartmentSchedule(BaseModel):
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    week_day = models.IntegerField(choices=WeekDayChoices.choices, validators=[MinValueValidator(1), MaxValueValidator(7)])
    time_from = models.TimeField()
    time_to = models.TimeField()

    class Meta:
        unique_together = ('department', 'week_day')

    def __str__(self):
        return f'{self.department} - {self.week_day}'


class EmployeeSchedule(BaseModel):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    week_day = models.IntegerField(choices=WeekDayChoices.choices, validators=[MinValueValidator(1), MaxValueValidator(7)])
    time_from = models.TimeField()
    time_to = models.TimeField()

    class Meta:
        unique_together = ('user', 'week_day')

    def __str__(self):
        return f'{self.user} - {self.week_day}'
