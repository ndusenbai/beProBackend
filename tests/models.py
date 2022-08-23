import datetime

from django.db import models

from utils.models import BaseModel


class TestTwoVersion(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'


class TestType(models.IntegerChoices):
    ONE_HEART_PRO = 1, '1. Heart PRO'
    TWO_BRAIN = 2, '2. Brain'
    THREE_BRAIN_PRO = 3, '3. Brain PRO'
    FOUR_HEART = 4, '4. Heart'


class TestStatus(models.IntegerChoices):
    AWAIT = 1, 'Await'
    FINISHED = 2, 'Finished'


class Test(BaseModel):
    test_type = models.IntegerField(choices=TestType.choices)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='tests')
    role = models.ForeignKey('companies.Role', on_delete=models.CASCADE, null=True)
    email = models.EmailField
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_man = models.BooleanField()
    finished_at = models.DateField(null=True)
    status = models.IntegerField(choices=TestStatus.choices, default=TestStatus.AWAIT)
