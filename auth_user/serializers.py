from datetime import date

from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import password_validation, get_user_model

from companies.models import Company
from utils.serializers import BaseSerializer

User = get_user_model()


class UserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'email', 'phone_number', 'selected_company_id')
        read_only_fields = ('id', 'email', 'is_admin')


class ChangePasswordSerializer(BaseSerializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.only('id'), required=False)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if 'user_id' in data:
            data['user'] = data.pop('user_id')
        return data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs.get('user', self.context['user'])
        password_validation.validate_password(attrs.get('new_password'), user)
        return attrs


class ForgotPasswordResetSerializer(BaseSerializer):
    password = serializers.CharField()

    def validate(self, attrs):
        attrs = super(ForgotPasswordResetSerializer, self).validate(attrs)
        password_validation.validate_password(attrs.get('password'))
        return attrs


class ForgotPasswordWithPinResetSerializer(BaseSerializer):
    code = serializers.IntegerField(min_value=1000, max_value=9999)
    password = serializers.CharField()

    def validate(self, attrs):
        attrs = super(ForgotPasswordWithPinResetSerializer, self).validate(attrs)
        password_validation.validate_password(attrs.get('password'))
        return attrs


class EmailSerializer(BaseSerializer):
    email = serializers.EmailField()


class UserSerializer(BaseSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    avatar = serializers.ImageField()


class EmployeeListSerializer(BaseSerializer):
    user = UserSerializer()
    role = serializers.IntegerField()
    grade = serializers.IntegerField()
    title = serializers.CharField()


class AssistantSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)
    phone_number = serializers.CharField()
    email = serializers.EmailField()
    assistant_type = serializers.IntegerField()


class AssistantUpdateSerializer(BaseSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)
    phone_number = serializers.CharField()
    assistant_type = serializers.IntegerField()


class ChangeSelectedCompanySerializer(BaseSerializer):
    new_selected_company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.only('id'))


class OwnerSerializer(BaseSerializer):
    id = serializers.IntegerField()
    last_name = serializers.CharField()
    first_name = serializers.CharField()
    middle_name = serializers.CharField()
    phone_number = serializers.CharField()
    company_name = serializers.CharField()
    employees_count = serializers.IntegerField()
    is_company_active = serializers.BooleanField()


class UserProfileSerializer(BaseSerializer):
    id = serializers.IntegerField(required=False, read_only=True)
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    email = serializers.EmailField(required=False, read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    role = serializers.SerializerMethodField(required=False)
    selected_company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.only('id'), required=False)
    score = serializers.SerializerMethodField()

    def get_role(self, instance):
        from auth_user.services import get_user_role
        try:
            return {
                'role_id': instance.role.id,
                'role': get_user_role(instance),
                'department_id': instance.role.department.id,
                'department_name': instance.role.department.name
            }
        except:
            return {
                'role_id': '',
                'role': '',
                'department_id': instance.role.department.id,
                'department_name': '',
            }

    def get_score(self, instance):
        now = timezone.now()
        first_date_of_month = date(now.year, now.month, 1)
        last_date_of_month = date(now.year, now.month + 1, 1)
        points = instance.role.scores.filter(created_at__range=[first_date_of_month, last_date_of_month]).values_list('points', flat=True)
        score = sum(point for point in points) + 100
        return score
