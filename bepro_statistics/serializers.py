from rest_framework import serializers
from django.contrib.auth import get_user_model

from bepro_statistics.models import Statistic, UserStatistic
from companies.models import Role, Department

from utils.serializers import BaseSerializer

User = get_user_model()


class StatisticSerializer(serializers.ModelSerializer):
    employees = serializers.ListSerializer(
        required=False,
        child=serializers.PrimaryKeyRelatedField(
            queryset=Role.objects.only('id')
        )
    )
    plan = serializers.IntegerField(required=False)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.only('id'), required=False)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.only('id'), required=False)

    class Meta:
        model = Statistic
        exclude = ('created_at', 'updated_at')


class GetStatisticSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    plan = serializers.IntegerField(required=False)
    role = serializers.PrimaryKeyRelatedField(read_only=True)
    role_name = serializers.SerializerMethodField(method_name="get_role")
    department = serializers.PrimaryKeyRelatedField(read_only=True)
    department_name = serializers.SerializerMethodField(method_name="get_department")

    def get_employees(self, obj):
        return obj.observers.select_related("role").only('role').values_list('role__id', flat=True)

    def get_full_name(self, obj):
        return obj.role.user.full_name if obj.role else ""

    def get_role(self, obj):
        return obj.role.get_role_display() if obj.role else ""

    def get_department(self, obj):
        return obj.department.name if obj.department else ""

    class Meta:
        model = Statistic
        exclude = ('created_at', 'updated_at')


class StatisticModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Statistic
        exclude = ('created_at', 'updated_at')


class UserStatisticModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserStatistic
        exclude = ('created_at', 'updated_at')


class UserStatsSerializer(BaseSerializer):
    day = serializers.DateField()
    fact = serializers.FloatField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['day_num'] = instance.day.weekday()
        if instance.statistic.statistic_type == 2:
            ret['plan'] = instance.statistic.plan
        return ret


class CreateUserStatSerializer(BaseSerializer):
    statistic_id = serializers.IntegerField()
    fact = serializers.IntegerField()


class ChangeUserStatSerializer(BaseSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.only('id'))
    statistic = serializers.PrimaryKeyRelatedField(queryset=Statistic.objects.only('id'))
    date = serializers.DateField()
    fact = serializers.IntegerField()


class StatsForUserSerializer(BaseSerializer):
    statistic = StatisticModelSerializer()
    user_statistics = UserStatsSerializer(many=True)


class HistoryStatsForUserSerializer(BaseSerializer):
    role_id = serializers.IntegerField()
    monday = serializers.DateField()
    sunday = serializers.DateField()
    statistic_types = serializers.ListField(child=serializers.CharField())

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['statistic_types'] = [int(i) for i in data['statistic_types'][0].split(',')]\
            if "," in data['statistic_types'][0] else [int(data['statistic_types'][0])]
        return data


class HistoryPdfStatsSerializer(BaseSerializer):
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.only('id'))
    monday = serializers.DateField()
    sunday = serializers.DateField()

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['role'] = data.pop('role_id')
        return data
