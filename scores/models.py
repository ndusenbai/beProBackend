from django.db import models
from django.contrib.auth import get_user_model

from utils.models import BaseModel

User = get_user_model()


class Reason(BaseModel):
    name = models.CharField(max_length=255)
    score = models.SmallIntegerField()
    is_auto = models.BooleanField()
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='reasons')

    def __str__(self):
        return f'{self.name}: {self.score}'


class Score(models.Model):
    role = models.ForeignKey('companies.Role', on_delete=models.CASCADE, related_name='scores')
    name = models.CharField(max_length=255)
    points = models.SmallIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.role}: {self.name} {self.points}'
