import json

from rest_framework import serializers

from tests.models import TestTwoVersion, Test
from utils.serializers import BaseSerializer


class TestOneSerializer(BaseSerializer):
    answers = serializers.ListField(child=serializers.IntegerField())
    is_man = serializers.BooleanField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if len(attrs['answers']) != 200:
            raise serializers.ValidationError({"answers": "Неправильное количество ответов"})
        return attrs


class TestTwoSerializer(BaseSerializer):
    answers = serializers.ListField(child=serializers.CharField())
    version = serializers.ChoiceField(choices=TestTwoVersion.choices)
    is_man = serializers.BooleanField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if len(attrs['answers']) != 80:
            raise serializers.ValidationError({"answers": "Неправильное количество ответов"})
        return attrs


class TestThreeSerializer(BaseSerializer):
    answers = serializers.JSONField()
    version = serializers.ChoiceField(choices=TestTwoVersion.choices)
    time = serializers.TimeField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['answers'] = json.loads(attrs['answers'])
        if len(attrs['answers']) != 12:
            raise serializers.ValidationError({"answers": "Неправильное количество ответов"})
        return attrs


class TestFourSerializer(BaseSerializer):
    answers = serializers.ListField(child=serializers.BooleanField())

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if len(attrs['answers']) != 105:
            raise serializers.ValidationError({"answers": "Неправильное количество ответов"})
        return attrs


class TestModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
