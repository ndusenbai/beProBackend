from django.db import models
from django.core.validators import MinValueValidator

from utils.models import BaseModel


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
