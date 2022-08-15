from django.db import models


class TestTwoVersion(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'
