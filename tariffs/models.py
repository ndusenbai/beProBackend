from django.db import models
from django.core.validators import MinValueValidator

from utils.models import BaseModel


class Tariff(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    max_capacity = models.IntegerField(validators=[MinValueValidator(0)])
    month_price = models.IntegerField()
    year_price = models.IntegerField()

    def __str__(self):
        return f'{self.name}, QTY: {self.max_capacity}'
