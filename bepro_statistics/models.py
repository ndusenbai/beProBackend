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


class PurposeType(models.IntegerChoices):
    TO_DEPARTMENT = 1, 'To department'
    TO_ROLE = 2, 'To role'


class Statistic(BaseModel):
    name = models.CharField(max_length=255)
    statistic_type = models.IntegerField(choices=StatisticType.choices, default=StatisticType.GENERAL)
    department = models.ForeignKey('companies.Department', on_delete=models.CASCADE, related_name='statistics', null=True, blank=True)
    role = models.ForeignKey('companies.Role', on_delete=models.CASCADE, related_name='statistics', null=True, blank=True)
    plan = models.FloatField(null=True, blank=True)
    visibility = models.IntegerField(choices=VisibilityType.choices)

    def __str__(self):
        return self.name


class StatisticObserver(BaseModel):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE, related_name='observers')
    role = models.ForeignKey('companies.Role', on_delete=models.CASCADE, related_name='observing_statistics')

    def __str__(self):
        return f'{self.statistic} - {self.role}'

    class Meta:
        unique_together = ('statistic', 'role')


class UserStatistic(BaseModel):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE)
    role = models.ForeignKey('companies.Role', on_delete=models.CASCADE)
    day = models.DateField()
    fact = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['statistic', 'role', 'day'], name='unique stat-role-day'),
        ]

    def __str__(self):
        return f'{self.role} - {self.day}: {self.fact}'

