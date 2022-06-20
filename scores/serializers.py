from rest_framework import serializers
from django.apps import apps
from django.contrib.auth import get_user_model

User = get_user_model()


class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model(
            app_label='scores',
            model_name='Reason'
        )
        fields = "__all__"


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model(
            app_label='scores',
            model_name='Score'
        )
        fields = "__all__"
