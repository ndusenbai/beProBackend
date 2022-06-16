from rest_framework import serializers

from companies.models import Company, Department, DepartmentSchedule, EmployeeSchedule
from utils.serializers import BaseSerializer


class CompanyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DepartmentModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DepartmentScheduleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentSchedule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UpdateDepartmentScheduleSerializer(BaseSerializer):
    time_from = serializers.TimeField()
    time_to = serializers.TimeField()


class EmployeeScheduleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeSchedule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UpdateEmployeeScheduleSerializer(BaseSerializer):
    time_from = serializers.TimeField()
    time_to = serializers.TimeField()
