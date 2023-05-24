from notifications.models import TestNotification
from rest_framework import serializers


class TestNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestNotification
        fields = "__alL__"
