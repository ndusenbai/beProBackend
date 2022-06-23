from rest_framework import serializers

from tariffs.models import Tariff


class TariffModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tariff
        exclude = ('created_at', 'updated_at')
        read_only_fields = ('id',)
