from rest_framework import serializers

from tariffs.models import Tariff
from utils.serializers import BaseSerializer


class TariffModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tariff
        exclude = ('created_at', 'updated_at')
        read_only_fields = ('id',)


class UpdateTariffSerializer(BaseSerializer):
    name = serializers.CharField()
    month_price = serializers.IntegerField()
    year_price = serializers.IntegerField()
