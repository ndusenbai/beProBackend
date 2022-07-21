import json
from datetime import datetime

from rest_framework import serializers

from auth_user.serializers import UserModelSerializer, UserSerializer
from companies.models import Company, Department, CompanyService
from timesheet.serializers import ScheduleSerializer
from utils.serializers import BaseSerializer


class CompanyServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyService
        fields = "__all__"


class CompanyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('id', 'owner_id', 'is_active', 'is_deleted', 'created_at', 'updated_at')


class CompanySerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    legal_name = serializers.CharField()
    years_of_work = serializers.IntegerField()
    is_active = serializers.BooleanField()
    max_employees_qty = serializers.IntegerField()
    owner_id = serializers.IntegerField(read_only=True)
    employees_count = serializers.IntegerField()
    employees_ratio = serializers.SerializerMethodField()

    def get_employees_ratio(self, instance):
        return f'{instance.employees_count}/{instance.max_employees_qty}'


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
    address = serializers.CharField(allow_blank=True)
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    radius = serializers.IntegerField(default=50)
    schedules = ScheduleSerializer(many=True)
    head_of_department = CreateHeadDepartmentSerializer(allow_null=True)


class UpdateDepartmentSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    address = serializers.CharField(allow_blank=True)
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    radius = serializers.IntegerField(default=50)
    schedules = ScheduleSerializer(many=True)
    head_of_department_id = serializers.IntegerField()


class DepartmentList2Serializer(DepartmentSerializer):
    head_of_department = UserModelSerializer()
    today_schedule = serializers.SerializerMethodField()
    employees_count = serializers.IntegerField()
    is_hr = serializers.BooleanField()

    def get_today_schedule(self, instance):
        week_day = datetime.today().weekday()
        today_schedule = instance.department_schedules.filter(week_day=week_day)
        if today_schedule:
            time_from = today_schedule[0].time_from.strftime('%H:%M')
            time_to = today_schedule[0].time_to.strftime('%H:%M')
            return f'{time_from} - {time_to}'
        return ''


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


class EmployeesSerializer(BaseSerializer):
    id = serializers.IntegerField()
    user = UserSerializer()
    role = serializers.IntegerField()
    grade = serializers.IntegerField()
    title = serializers.CharField()
    score = serializers.IntegerField()
    department = DepartmentListSerializer()
    schedules = ScheduleSerializer(many=True)
    today_schedule = serializers.SerializerMethodField()

    def get_today_schedule(self, instance):
        try:
            week_day = datetime.today().weekday()
            today_schedule = list(filter(lambda p: p.week_day == week_day, instance.schedules))[0]
            time_from = today_schedule.time_from.strftime('%H:%M')
            time_to = today_schedule.time_to.strftime('%H:%M')
            return f'{time_from} - {time_to}'
        except IndexError:
            return ''


class CreateEmployeeSerializer(BaseSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_blank=True)
    avatar = serializers.ImageField(allow_null=True)
    title = serializers.CharField()
    grade = serializers.IntegerField()
    department_id = serializers.IntegerField()
    schedules = ScheduleSerializer(many=True)

    def to_internal_value(self, data):
        if hasattr(data, 'getlist'):
            data = data.dict()
        if isinstance(data['schedules'], str):
            data['schedules'] = json.loads(data['schedules'])
        data = super().to_internal_value(data)
        return data


class FilterEmployeesSerializer(BaseSerializer):
    departments = serializers.ListField(child=serializers.CharField(), required=False)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if 'departments' in data:
            data['departments'] = [int(i) for i in data['departments'][0].split(',')]
        return data
