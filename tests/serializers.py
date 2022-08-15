from rest_framework import serializers

from utils.serializers import BaseSerializer


class TestFourSerializer(BaseSerializer):
    answers = serializers.ListField(child=serializers.BooleanField())

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if len(attrs['answers']) != 105:
            raise serializers.ValidationError({"message": "Неправильное количество ответов"})
        return attrs

