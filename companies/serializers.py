from rest_framework import serializers

from companies.models import Company, Department, Schedule
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


class ScheduleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UpdateScheduleSerializer(BaseSerializer):
    time_from = serializers.TimeField()
    time_to = serializers.TimeField()
