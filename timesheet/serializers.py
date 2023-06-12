from rest_framework import serializers

from companies.models import Role
from timesheet.models import TimeSheet, DepartmentSchedule, EmployeeSchedule, TimeSheetChoices
from utils.serializers import BaseSerializer


class TimeSheetModelSerializer(serializers.ModelSerializer):
    status_decoded = serializers.SerializerMethodField(read_only=True)
    timezone_schedule = serializers.SerializerMethodField(read_only=True)
    working_hours = serializers.SerializerMethodField(read_only=True)

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

    def get_working_hours(self, instance):
        if instance.check_in_new is None or instance.check_out_new is None or instance.status not in [1, 2]:
            return ''
        time_diff = instance.check_out_new - instance.check_in_new
        return time_diff.total_seconds() / 3600


class TimeSheetListSerializer(BaseSerializer):
    role_id = serializers.IntegerField(required=False)
    month = serializers.IntegerField(min_value=1, max_value=12, required=False)
    year = serializers.IntegerField(min_value=2022, max_value=9999, required=False)


class TimeSheetUpdateSerializer(BaseSerializer):
    check_in = serializers.TimeField(format='%Y-%m-%dT%H:%M:%S%z', required=False)
    check_out = serializers.TimeField(format='%Y-%m-%dT%H:%M:%S%z', required=False)
    status = serializers.IntegerField(required=False)
    time_from = serializers.TimeField(format='%H:%M', required=False)
    time_to = serializers.TimeField(format='%H:%M', required=False)


class CheckInSerializer(BaseSerializer):
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    check_in = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')
    file = serializers.FileField(allow_null=True, required=False)
    comment = serializers.CharField(allow_null=True, required=False)


class TakeTimeOffSerializer(BaseSerializer):
    check_out = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')
    comment = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    file = serializers.FileField(required=False, allow_null=True, allow_blank=True)


class CheckOutSerializer(BaseSerializer):
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    check_out = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z')


class ScheduleSerializer(BaseSerializer):
    week_day = serializers.IntegerField(min_value=0, max_value=6)
    time_from = serializers.TimeField(format='%H:%M')
    time_to = serializers.TimeField(format='%H:%M')
    timezone = serializers.RegexField(r'^\+\d{2,2}:\d{2,2}\b', read_only=True)
    is_night_shift = serializers.BooleanField(default=False)


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


class CreateFutureTimeSheetSerializer(BaseSerializer):
    role_id = serializers.IntegerField()
    day = serializers.IntegerField(min_value=1, max_value=31)
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2022, max_value=9999)
    status = serializers.ChoiceField(choices=[timesheet_choice for timesheet_choice in TimeSheetChoices.choices])
    time_from = serializers.TimeField(required=False, allow_null=True)
    time_to = serializers.TimeField(required=False, allow_null=True)


class MonthHoursSerializer(BaseSerializer):
    month = serializers.DateTimeField()
    total_duration = serializers.FloatField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['total_duration'] = round(ret['total_duration'], 2)
        return ret


class MonthHoursValidationSerializer(BaseSerializer):
    year = serializers.IntegerField(required=False)
    months = serializers.ListField(child=serializers.CharField(), required=False,)
    role = serializers.IntegerField()

    def to_internal_value(self, data):
        if 'months' in data:
            data = super().to_internal_value(data)
            data['months'] = [int(i) for i in data['months'][0].split(',')]
        return data


class UpdateTimeSheetSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeSheet
        fields = ("status", "time_from", "time_to")
