from rest_framework import serializers

from applications.models import ApplicationStatus
from companies.models import Company, Role
from companies.serializers import CompanyServiceSerializer, CompanyModelSerializer
from tariffs.models import Tariff, TariffPeriod, TestPrice
from utils.serializers import BaseSerializer


class TariffModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tariff
        exclude = ('created_at', 'updated_at')
        read_only_fields = ('id',)


class TestPriceModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestPrice
        exclude = ('id', 'created_at', 'updated_at')


class UpdateTariffSerializer(BaseSerializer):
    name = serializers.CharField()
    month_price = serializers.IntegerField()
    year_price = serializers.IntegerField()


class MyTariffSerializer(BaseSerializer):
    tariff = TariffModelSerializer()
    period = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    employees_ratio = serializers.SerializerMethodField()
    companies = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def get_period(self, instance):
        if instance.period == TariffPeriod.MONTHLY:
            return 'monthly'
        elif instance.period == TariffPeriod.YEARLY:
            return 'yearly'

    def get_price(self, instance):
        if instance.period == TariffPeriod.MONTHLY:
            return instance.tariff.month_price
        elif instance.period == TariffPeriod.YEARLY:
            return instance.tariff.year_price

    def get_status(self, instance):
        return ApplicationStatus.get_status(instance.status)

    def get_employees_ratio(self, instance):
        owner_companies = Company.objects.filter(owner=instance.owner).values_list('id', flat=True)
        total_employees_count = Role.objects.filter(company__in=owner_companies).count()
        return f'{total_employees_count}/{instance.tariff.max_employees_qty}'

    def get_companies(self, instance):
        return CompanyModelSerializer(Company.objects.filter(owner=instance.owner), many=True).data

    def get_services(self, instance):
        return CompanyServiceSerializer(instance.owner.selected_company.service).data


class ChangeTariff(BaseSerializer):
    tariff = serializers.PrimaryKeyRelatedField(queryset=Tariff.objects.only('id'))
    period = serializers.ChoiceField(choices=TariffPeriod.choices)
    is_instant_apply = serializers.BooleanField(default=False, required=False)
