import json

from rest_framework import serializers

from companies.models import Company
from tests.models import TestTwoVersion, Test, TestType, Genders
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

    def to_internal_value(self, data):
        data['answers'] = json.dumps(data['answers'])
        data = super().to_internal_value(data)
        return data


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


class CreateTestSerializer(BaseSerializer):
    test_type = serializers.ChoiceField(choices=TestType.choices)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.only('id'), required=False)
    email = serializers.EmailField(allow_blank=True)
    phone_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField(allow_blank=True)
    date_of_birth = serializers.DateField(allow_null=True)
    job_title = serializers.CharField()
    version = serializers.ChoiceField(choices=TestTwoVersion.choices, allow_blank=True)
    force_version = serializers.BooleanField(required=False, default=False)


class SubmitTestSerializer(BaseSerializer):
    gender = serializers.ChoiceField(choices=Genders.choices, required=False)
    hobbies = serializers.CharField(required=False)
    test_data = serializers.DictField()


class SubmitTestResponseSerializer(BaseSerializer):
    link = serializers.CharField()
    whatsapp_link = serializers.CharField()
    uid = serializers.CharField()
