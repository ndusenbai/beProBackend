from django.db import models
from utils.models import BaseModel


class AppVersion(BaseModel):
    android_version = models.CharField(max_length=250)
    ios_version = models.CharField(max_length=250)

    def __str__(self):
        return 'App Version'
