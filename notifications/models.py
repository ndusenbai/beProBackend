from django.db import models
from utils.models import BaseModel


class EmployeeNotification(BaseModel):
    role = models.ForeignKey('companies.Role', on_delete=models.CASCADE, related_name='notifications')
    check_in_notified = models.BooleanField(default=False)
    check_out_notified = models.BooleanField(default=False)


class TestNotification(BaseModel):
    role_id = models.PositiveIntegerField()
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=250)
