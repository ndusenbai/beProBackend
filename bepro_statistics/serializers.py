from rest_framework import serializers
from bepro_statistics.models import Statistic, UserStatistic
from django.contrib.auth import get_user_model

from utils.serializers import BaseSerializer

User = get_user_model()


class StatisticSerializer(serializers.ModelSerializer):
    employees = serializers.ListSerializer(
        write_only=True,
        child=serializers.PrimaryKeyRelatedField(
            queryset=User.objects.only('id')
        )
    )

    class Meta:
        model = Statistic
        exclude = ('created_at', 'updated_at')


class UserStatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserStatistic
        exclude = ('created_at', 'updated_at')


class UserStatsSerializer(BaseSerializer):
    weekday = serializers.DateField()
    fact = serializers.FloatField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.statistic.statistic_type == 2:
            ret['plan'] = instance.statistic.plan
        return ret
