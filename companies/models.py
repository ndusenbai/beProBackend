from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from utils.models import BaseModel

User = get_user_model()


class CompanyTypes(models.IntegerChoices):
    LLC = 1, 'Limited Liability Company'
    SP = 2, 'Sole Proprietorship'


class RoleChoices(models.IntegerChoices):
    OWNER = 1, _('Owner')
    HR = 2, _('HR')
    OBSERVER = 3, _('Observer')
    EMPLOYEE = 4, _('Employee')


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
    radius = models.IntegerField(default=50)

    def __str__(self):
        return f'{self.name} @{self.company}'


class Role(BaseModel):
    company = models.ForeignKey(to=Company, on_delete=models.CASCADE)
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE, null=True, blank=True)
    role = models.IntegerField(choices=RoleChoices.choices, default=RoleChoices.EMPLOYEE)
    user = models.ForeignKey(to='auth_user.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='')
    grade = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company', 'role', 'user'], name='unique role in company for user'),
            models.UniqueConstraint(fields=['department', 'role', 'user'], name='unique role in department for user')
        ]
