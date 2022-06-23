from django.db import models
from utils.models import BaseModel
from django.contrib.auth import get_user_model
User = get_user_model()


class StatisticType(models.IntegerChoices):
    GENERAL = 1, 'General statistics'
    DOUBLE = 2, 'Double statistics'
    INVERTED = 3, 'Inverted statistics'


class VisibilityType(models.IntegerChoices):
    OPEN_EVERYONE = 1, 'Open to everyone'
    OPEN_DEPARTMENT = 2, 'Open by department'
    HIDDEN = 3, 'Hidden'
    EMPLOYEES = 4, 'Employees'


class Statistic(BaseModel):
    name = models.CharField(max_length=255)
    statistic_type = models.IntegerField(choices=StatisticType.choices, default=StatisticType.GENERAL)
    department = models.ForeignKey(
        'companies.Department',
        on_delete=models.CASCADE,
        related_name='statistics',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='statistics',
        null=True,
        blank=True
    )
    plan = models.FloatField(null=True, blank=True)
    visibility = models.IntegerField(choices=VisibilityType.choices)

    def __str__(self):
        return self.name


class StatisticObserver(BaseModel):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE, related_name='observers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='observing_statistics')

    def __str__(self):
        return f'{self.statistic} - {self.user}'


class UserStatistic(BaseModel):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_statistics')
    weekday = models.DateField()
    fact = models.FloatField()

    def __str__(self):
        return f'{self.user} - {self.weekday}: {self.fact}'
