from rest_framework import serializers

from timesheet.models import TimeSheet, DepartmentSchedule, EmployeeSchedule, TimeSheetChoices
from utils.serializers import BaseSerializer


class TimeSheetModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeSheet
        exclude = ('created_at', 'updated_at')


class TimeSheetListSerializer(BaseSerializer):
    role_id = serializers.IntegerField(required=False)
    month = serializers.IntegerField(min_value=1, max_value=12, required=False)
    year = serializers.IntegerField(min_value=2022, max_value=9999, required=False)


class TimeSheetUpdateSerializer(BaseSerializer):
    check_in = serializers.TimeField(format='%Y-%m-%dT%H:%M:%S%z', required=False)
    check_out = serializers.TimeField(format='%Y-%m-%dT%H:%M:%S%z', required=False)
    status = serializers.IntegerField(required=False)


class CheckInSerializer(BaseSerializer):
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    check_in = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')
    comment = serializers.CharField(allow_blank=True, required=False)
    file = serializers.FileField(allow_null=True, required=False)


class TakeTimeOffSerializer(BaseSerializer):
    comment = serializers.CharField(allow_blank=True, required=False)


class CheckOutSerializer(BaseSerializer):
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    check_out = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')


class ScheduleSerializer(BaseSerializer):
    week_day = serializers.IntegerField(min_value=0, max_value=6)
    time_from = serializers.TimeField(format='%H:%M')
    time_to = serializers.TimeField(format='%H:%M')


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


class ChangeTimeSheetSerializer(BaseSerializer):
    timesheet = serializers.PrimaryKeyRelatedField(queryset=TimeSheet.objects.only('id'))
    start_vacation_date = serializers.DateField(allow_null=True)
    end_vacation_date = serializers.DateField(allow_null=True)
    status = serializers.ChoiceField(choices=TimeSheetChoices.choices)
