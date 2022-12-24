from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from utils.models import BaseModel

User = get_user_model()


class RoleChoices(models.IntegerChoices):
    HR = 1, _('HR')
    OBSERVER = 2, _('Observer')
    EMPLOYEE = 3, _('Employee')
    HEAD_OF_DEPARTMENT = 4, _('Head of department')


class Company(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    legal_name = models.CharField(max_length=100, unique=True)
    years_of_work = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    max_employees_qty = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, default=None, related_name='owned_companies')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class Department(BaseModel):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(to=Company, on_delete=models.CASCADE, related_name='departments')
    address = models.CharField(max_length=200, blank=True)
    is_manual_address = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=22, decimal_places=6, default=0, validators=[MinValueValidator(0)])
    longitude = models.DecimalField(max_digits=22, decimal_places=6, default=0, validators=[MinValueValidator(0)])
    is_hr = models.BooleanField(default=False)
    radius = models.IntegerField(default=50)
    head_of_department = models.ForeignKey(to='companies.Role', on_delete=models.SET_NULL, null=True, blank=True, related_name='head_departments')
    timezone = models.CharField(max_length=10, default='+06:00')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'company'], name='unique name-company'),
        ]

    def __str__(self):
        return f'{self.name} @{self.company}'


class Role(BaseModel):
    company = models.ForeignKey(to=Company, on_delete=models.CASCADE, related_name='roles')
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE, null=True, blank=True, related_name='roles')
    role = models.IntegerField(choices=RoleChoices.choices, default=RoleChoices.EMPLOYEE)
    user = models.OneToOneField(to='auth_user.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='')
    grade = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        department = self.department or '-'
        return f'{self.user} - {department}'


class CompanyService(BaseModel):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='service')
    analytics_enabled = models.BooleanField(default=True)
    time_tracking_enabled = models.BooleanField(default=True)
    tests_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'Service of {self.company}'
