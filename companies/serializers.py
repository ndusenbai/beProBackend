import json
from datetime import datetime

from rest_framework import serializers
from auth_user.serializers import UserModelSerializer, UserSerializer
from companies.models import Company, Department, CompanyService
from timesheet.serializers import ScheduleSerializer
from utils.serializers import BaseSerializer


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


class CompanyServiceSerializer(serializers.ModelSerializer):
    company = CompanyModelSerializer()

    class Meta:
        model = CompanyService
        fields = "__all__"


class CompanyServiceUpdateSerializer(BaseSerializer):
    analytics_enabled = serializers.BooleanField()
    time_tracking_enabled = serializers.BooleanField()
    tests_enabled = serializers.BooleanField()
    id = serializers.IntegerField()


class CompanyServicesUpdateSerializer(BaseSerializer):
    company_services = CompanyServiceUpdateSerializer(many=True)


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
    is_manual_address = serializers.BooleanField(default=False, required=False)
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    radius = serializers.IntegerField(default=50)
    schedules = ScheduleSerializer(many=True)
    head_of_department = CreateHeadDepartmentSerializer(allow_null=True)

    def validate(self, attrs):
        if not attrs.get('address'):
            raise serializers.ValidationError({"address": "Введите адрес"})
        return attrs


class UpdateDepartmentSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    address = serializers.CharField(allow_blank=True)
    is_manual_address = serializers.BooleanField(default=False, required=False)
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6, default=0)
    radius = serializers.IntegerField(default=50)
    schedules = ScheduleSerializer(many=True)
    head_of_department_id = serializers.IntegerField(allow_null=True)


class HeadOfDepartmentSerializer(BaseSerializer):
    id = serializers.IntegerField()
    last_name = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    middle_name = serializers.SerializerMethodField()

    def get_last_name(self, instance):
        return instance.user.last_name

    def get_first_name(self, instance):
        return instance.user.first_name

    def get_middle_name(self, instance):
        return instance.user.middle_name


class DepartmentList2Serializer(DepartmentSerializer):
    head_of_department = HeadOfDepartmentSerializer()
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
    latitude = serializers.DecimalField(max_digits=22, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=6)


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
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    middle_name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    phone_number = serializers.CharField(allow_blank=True)
    avatar = serializers.ImageField(allow_null=True, required=False)
    title = serializers.CharField()
    grade = serializers.IntegerField()
    department_id = serializers.IntegerField()
    schedules = ScheduleSerializer(many=True,)

    def to_internal_value(self, data):
        if hasattr(data, 'getlist'):
            data = data.dict()
        if isinstance(data['schedules'], str):
            data['schedules'] = json.loads(data['schedules'])
        if 'avatar' in data and isinstance(data['avatar'], str) and data['avatar'] == 'null':
            data['avatar'] = None
        data['phone_number'] = data['phone_number'].replace(' ', '').replace('(', '').replace(')', '')
        data = super().to_internal_value(data)
        return data

    def validate(self, attrs):
        validation_errors = []

        if ('first_name' in attrs and not attrs.get('first_name')) or \
                ('last_name' in attrs and not attrs.get('last_name')):
            validation_errors.append({'name': 'Введите ФИО'})

        if 'email' in attrs and not attrs.get('email'):
            validation_errors.append({'email': 'Введите Email'})

        if 'title' in attrs and not attrs.get('title'):
            validation_errors.append({'title': 'Введите позицию'})

        if 'grade' in attrs and not attrs.get('grade'):
            validation_errors.append({'grade': 'Укажите градацию'})

        if 'schedules' in attrs and not attrs.get('schedules'):
            validation_errors.append({'schedules': 'Укажите часы работы'})

        if 'department_id' in attrs and not attrs.get('department_id'):
            validation_errors.append({'department_id': 'Укажите отдел'})

        if validation_errors:
            raise serializers.ValidationError(validation_errors)

        return attrs


class FilterEmployeesSerializer(BaseSerializer):
    departments = serializers.ListField(child=serializers.CharField(), required=False)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if 'departments' in data:
            data['departments'] = [int(i) for i in data['departments'][0].split(',')]
        return data


class ObserverListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    user = UserSerializer()
    company = CompanyModelSerializer()


class ObserverCreateSerializer(BaseSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)
    email = serializers.EmailField()
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.only('id'))


class ObserverUpdateSerializer(BaseSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)


class RetrieveCompanyServiceSerializer(BaseSerializer):
    analytics_enabled = serializers.BooleanField()
    time_tracking_enabled = serializers.BooleanField()
    tests_enabled = serializers.BooleanField()
