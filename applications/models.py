from django.db import models
from django.core.validators import MinValueValidator
from utils.models import BaseModel

from django.contrib.auth import get_user_model
User = get_user_model()


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


class TariffApplication(BaseModel):
    # Temporary replacement for fk to Tariff's
    tariff = models.PositiveSmallIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tariff_applications')
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.NEW)


class TestApplication(BaseModel):
    # Temporary replacement for fk to Test's
    test = models.PositiveSmallIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_applications')
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.NEW)

