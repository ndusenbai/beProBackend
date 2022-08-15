from rest_framework import serializers

from tests.models import TestTwoVersion
from utils.serializers import BaseSerializer


class TestFourSerializer(BaseSerializer):
    answers = serializers.ListField(child=serializers.BooleanField())

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if len(attrs['answers']) != 105:
            raise serializers.ValidationError({"answers": "Неправильное количество ответов"})
        return attrs


class TestTwoSerializer(BaseSerializer):
    answers = serializers.ListField(child=serializers.CharField())
    version = serializers.ChoiceField(choices=TestTwoVersion.choices)
    sex = serializers.BooleanField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if len(attrs['answers']) != 80:
            raise serializers.ValidationError({"answers": "Неправильное количество ответов"})
        return attrs

