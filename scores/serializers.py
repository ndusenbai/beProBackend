from rest_framework import serializers
from django.apps import apps
from django.contrib.auth import get_user_model

from auth_user.serializers import UserSerializer
from utils.serializers import BaseSerializer

User = get_user_model()


class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model(
            app_label='scores',
            model_name='Reason'
        )
        fields = "__all__"


class ScoreModelSerializer(serializers.ModelSerializer):
    reason = ReasonSerializer()
    created_by = UserSerializer()

    class Meta:
        model = apps.get_model(
            app_label='scores',
            model_name='Score'
        )
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ScoreSerializer(BaseSerializer):
    role_id = serializers.IntegerField()
    reason_id = serializers.IntegerField()


class MonthScoresValidationSerializer(BaseSerializer):
    year = serializers.IntegerField()
    months = serializers.ListField(child=serializers.CharField())
    role = serializers.IntegerField()

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['months'] = [int(i) for i in data['months'][0].split(',')]
        return data


class MonthScoresSerializer(BaseSerializer):
    month = serializers.DateTimeField()
    score = serializers.IntegerField()
