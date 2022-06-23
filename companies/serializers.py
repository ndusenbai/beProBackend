from datetime import datetime

from rest_framework import serializers

from auth_user.serializers import UserModelSerializer
from companies.models import Company, Department
from timesheet.serializers import ScheduleSerializer
from utils.serializers import BaseSerializer


class CompanyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class CreateHeadDepartmentSerializer(BaseSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_blank=True)
    title = serializers.CharField()
    grade = serializers.IntegerField(min_value=1, max_value=4)


class DepartmentSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    address = serializers.CharField()
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    schedules = ScheduleSerializer(many=True)
    head_of_department = CreateHeadDepartmentSerializer(allow_null=True)


class DepartmentList2Serializer(DepartmentSerializer):
    head_of_department = UserModelSerializer()
    today_schedule = serializers.SerializerMethodField()

    def get_today_schedule(self, instance):
        week_day = datetime.today().weekday()
        today_schedule = instance.department_schedules.filter(week_day=week_day)
        if today_schedule:
            time_from = today_schedule[0].time_from.strftime('%H:%M')
            time_to = today_schedule[0].time_to.strftime('%H:%M')
            return f'{time_from} - {time_to}'
        return '-'


class DepartmentModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        exclude = ('created_at', 'updated_at')


class DepartmentListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class RoleSerializer(BaseSerializer):
    company = CompanyModelSerializer()
    department = DepartmentModelSerializer()
    role = serializers.CharField()
    title = serializers.CharField()
    grade = serializers.IntegerField()
