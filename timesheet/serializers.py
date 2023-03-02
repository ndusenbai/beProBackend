from rest_framework import serializers

from companies.models import Role
from timesheet.models import TimeSheet, DepartmentSchedule, EmployeeSchedule, TimeSheetChoices
from utils.serializers import BaseSerializer


class TimeSheetModelSerializer(serializers.ModelSerializer):
    status_decoded = serializers.SerializerMethodField(read_only=True)
    timezone_schedule = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TimeSheet
        exclude = ('created_at', 'updated_at')

    def get_timezone_schedule(self, instance):
        if instance.role:
            if instance.role.department:
                if instance.role.department.timezone:
                    return instance.role.department.timezone
        return '+00:00'

    def get_status_decoded(self, instance):
        return TimeSheetChoices.get_status(instance.status)


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
    check_out = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')


class ScheduleSerializer(BaseSerializer):
    week_day = serializers.IntegerField(min_value=0, max_value=6)
    time_from = serializers.TimeField(format='%H:%M')
    time_to = serializers.TimeField(format='%H:%M')
    timezone = serializers.RegexField(r'^\+\d{2,2}:\d{2,2}\b', read_only=True)


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
    status = serializers.ChoiceField(choices=[timesheet_choice for timesheet_choice in TimeSheetChoices.choices
                                              if timesheet_choice[0] != TimeSheetChoices.ON_VACATION])


class VacationTimeSheetSerializer(BaseSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.only('id'))
    start_vacation_date = serializers.DateField()
    end_vacation_date = serializers.DateField()


class UpdateFutureTimeSheetSerializer(BaseSerializer):
    role_id = serializers.IntegerField(required=False)
    day = serializers.IntegerField(min_value=1, max_value=31)
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2022, max_value=9999)
