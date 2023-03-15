from rest_framework import serializers
from django.contrib.auth import get_user_model

from auth_user.serializers import UserSerializer
from scores.models import Score, Reason
from utils.serializers import BaseSerializer

User = get_user_model()


class ReasonSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(min_value=-100, max_value=100)

    class Meta:
        model = Reason
        fields = "__all__"


class ScoreModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    points = serializers.IntegerField()
    created_by = UserSerializer()

    class Meta:
        model = Score
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ScoreSerializer(BaseSerializer):
    role_id = serializers.IntegerField()
    reason_id = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class MonthScoresValidationSerializer(BaseSerializer):
    year = serializers.IntegerField(required=False)
    months = serializers.ListField(child=serializers.CharField(), required=False,)
    role = serializers.IntegerField()

    def to_internal_value(self, data):
        if 'months' in data:
            data = super().to_internal_value(data)
            data['months'] = [int(i) for i in data['months'][0].split(',')]
        return data


class MonthScoresSerializer(BaseSerializer):
    month = serializers.DateTimeField()
    score = serializers.IntegerField()


class ScoreRoleSerializer(BaseSerializer):
    full_name = serializers.SerializerMethodField()
    title = serializers.CharField()
    role = serializers.IntegerField()

    def get_user(self, instance):
        return instance.user.full_name


class ScoreFeedSerializer(serializers.ModelSerializer):
    role = ScoreRoleSerializer()

    class Meta:
        model = Score
        fields = "__all__"
