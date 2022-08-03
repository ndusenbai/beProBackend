from django.db import models
from django.core.validators import MinValueValidator

from tariffs.models import TariffPeriod
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
    max_employees_qty = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    years_of_work = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    tariff_id = models.IntegerField(validators=[MinValueValidator(0)])
    period = models.PositiveSmallIntegerField(choices=TariffPeriod.choices)
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.NEW)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.company_name}: {self.last_name} {self.first_name}'


class TariffApplication(BaseModel):
    tariff = models.ForeignKey(to='tariffs.Tariff', on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tariff_applications')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    period = models.PositiveSmallIntegerField(choices=TariffPeriod.choices)
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.NEW)

    def __str__(self):
        return f'{self.owner} tariff:{self.owner} status:{self.status}'


class TestApplication(BaseModel):
    # Temporary replacement for fk to Test's
    test = models.PositiveSmallIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_applications')
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.NEW)

