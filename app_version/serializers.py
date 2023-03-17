from .models import AppVersion
from rest_framework import serializers


class AppVersionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppVersion
        exclude = ('created_at', 'updated_at')
