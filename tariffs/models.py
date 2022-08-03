from django.db import models
from django.core.validators import MinValueValidator

from utils.models import BaseModel


class TariffPeriod(models.IntegerChoices):
    MONTHLY = 1, 'Monthly'
    YEARLY = 2, 'Yearly'


class Tariff(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    max_employees_qty = models.IntegerField(validators=[MinValueValidator(0)])
    month_price = models.IntegerField()
    year_price = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}, QTY: {self.max_employees_qty}'
