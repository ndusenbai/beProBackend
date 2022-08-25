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


class Genders(models.IntegerChoices):
    MALE = 1, 'Male'
    FEMALE = 0, 'Female'


class Test(BaseModel):
    FREE_TESTS = [TestType.TWO_BRAIN, TestType.FOUR_HEART]
    PAID_TESTS = [TestType.ONE_HEART_PRO, TestType.THREE_BRAIN_PRO]

    test_type = models.IntegerField(choices=TestType.choices)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='tests', null=True, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, default='')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    gender = models.PositiveSmallIntegerField(choices=Genders.choices, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=300, blank=True)
    hobbies = models.TextField(blank=True)
    version = models.CharField(choices=TestTwoVersion.choices, max_length=1, blank=True)
    finished_at = models.DateField(null=True, blank=True)
    status = models.IntegerField(choices=TestStatus.choices, default=TestStatus.AWAIT)
    result = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ('-created_at',)
