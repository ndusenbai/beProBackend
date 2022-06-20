from rest_framework import serializers
from bepro_statistics.models import Statistic
from django.contrib.auth import get_user_model
User = get_user_model()


class StatisticSerializer(serializers.ModelSerializer):
    employees = serializers.ListSerializer(
        write_only=True,
        child=serializers.PrimaryKeyRelatedField(
            queryset=User.objects.only('id')
        )
    )

    class Meta:
        model = Statistic
        exclude = ('company',)




