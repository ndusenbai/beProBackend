from rest_framework import serializers
from django.contrib.auth import password_validation

from auth_user.models import User
from utils.serializers import BaseSerializer


class UserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'email', 'phone_number', 'is_admin')
        read_only_fields = ('id', 'email', 'is_admin')


class ChangePasswordSerializer(BaseSerializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        password_validation.validate_password(attrs.get('new_password'))
        return attrs


class ForgotPasswordResetSerializer(BaseSerializer):
    password = serializers.CharField()

    def validate(self, attrs):
        attrs = super(ForgotPasswordResetSerializer, self).validate(attrs)
        password_validation.validate_password(attrs.get('password'))
        return attrs


class EmailSerializer(BaseSerializer):
    email = serializers.EmailField()

