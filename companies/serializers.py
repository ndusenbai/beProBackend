from rest_framework import serializers

from companies.models import Company, DepartmentSchedule, EmployeeSchedule, Department
from utils.serializers import BaseSerializer


class CompanyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ScheduleSerializer(BaseSerializer):
    week_day = serializers.IntegerField()
    time_from = serializers.TimeField()
    time_to = serializers.TimeField()


class DepartmentSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    address = serializers.CharField()
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    schedules = ScheduleSerializer(many=True)


class DepartmentModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        exclude = ('created_at', 'updated_at')


class DepartmentScheduleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentSchedule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UpdateDepartmentScheduleSerializer(BaseSerializer):
    schedules = ScheduleSerializer(many=True)


class EmployeeScheduleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeSchedule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UpdateEmployeeScheduleSerializer(BaseSerializer):
    time_from = serializers.TimeField()
    time_to = serializers.TimeField()


class DepartmentListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class RoleSerializer(BaseSerializer):
    company = CompanyModelSerializer()
    department = DepartmentModelSerializer()
    role = serializers.CharField()
    title = serializers.CharField()
    grade = serializers.IntegerField()
