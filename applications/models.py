from django.db import models
from django.core.validators import MinValueValidator

from utils.models import BaseModel


class ApplicationStatus(models.IntegerChoices):
    NEW = 1, 'New'
    ACCEPTED = 2, 'Accepted'
    DECLINED = 3, 'Declined'


class ApplicationToCreateCompany(BaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=200)
    company_legal_name = models.CharField(max_length=200)
    employees_qty = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    years_of_work = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.NEW)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.company_name}: {self.last_name} {self.first_name}'
