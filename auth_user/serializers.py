from rest_framework import serializers
from django.contrib.auth import password_validation, get_user_model

from timesheet.serializers import ScheduleSerializer
from utils.serializers import BaseSerializer

User = get_user_model()


class UserSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField(allow_blank=True)
    email = serializers.CharField()
    phone_number = serializers.CharField()
    schedules = ScheduleSerializer(many=True)


class CreateEmployeeSerializer(BaseSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_blank=True)
    title = serializers.CharField()
    grade = serializers.IntegerField()
    department_id = serializers.IntegerField()
    schedules = ScheduleSerializer(many=True)


class UserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'email', 'phone_number', 'selected_company_id')
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


class ObserverCreateSerializer(BaseSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)
    email = serializers.EmailField()


class UserSerializer(BaseSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)
    email = serializers.EmailField()
    avatar = serializers.ImageField()


class ObserverListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    user = UserSerializer()


class EmployeeListSerializer(BaseSerializer):
    user = UserSerializer()
    role = serializers.IntegerField()
    grade = serializers.IntegerField()
    title = serializers.CharField()


class EmployeesSerializer(EmployeeListSerializer):
    score = serializers.IntegerField()
    department_name = serializers.SerializerMethodField()

    def get_department_name(self, instance):
        try:
            return instance.department.name
        except AttributeError:
            return ''


class AssistantSerializer(BaseSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)
    phone_number = serializers.CharField()
    email = serializers.EmailField()
    assistant_type = serializers.IntegerField()
