from rest_framework import serializers
from django.contrib.auth import password_validation

from utils.serializers import BaseSerializer


class ChangePasswordSerializer(BaseSerializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        password_validation.validate_password(attrs.get('new_password'))
        return attrs
