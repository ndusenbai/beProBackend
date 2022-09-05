from rest_framework import serializers

from applications.models import ApplicationToCreateCompany, ApplicationStatus, TariffApplication, TestApplication, \
    TestApplicationStatus
from auth_user.serializers import UserModelSerializer
from companies.serializers import CompanyServiceSerializer
from tariffs.models import Tariff, TariffPeriod
from tariffs.serializers import TariffModelSerializer
from utils.serializers import BaseSerializer


class TariffApplicationSerializer(serializers.ModelSerializer):
    tariff = TariffModelSerializer(required=False)
    owner = UserModelSerializer(required=False)
    period = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = TariffApplication
        fields = '__all__'

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


class TariffApplicationRetrieveSerializer(TariffApplicationSerializer):
    services = serializers.SerializerMethodField()

    def get_services(self, instance):
        return CompanyServiceSerializer(instance.owner.selected_company.service).data


class TestApplicationModelSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = TestApplication
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_owner(self, instance):
        return UserModelSerializer(instance.company.owner).data


class ApplicationToCreateCompanyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationToCreateCompany
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class CreateApplicationToCreateCompanySerializer(BaseSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField(allow_blank=True, default='')
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_blank=True, default='')
    company_name = serializers.CharField()
    company_legal_name = serializers.CharField()
    max_employees_qty = serializers.IntegerField(default=0)
    years_of_work = serializers.IntegerField(default=0)
    tariff_id = serializers.PrimaryKeyRelatedField(queryset=Tariff.objects.only('id'))
    period = serializers.ChoiceField(choices=TariffPeriod)


class UpdateApplicationStatus(BaseSerializer):
    status = serializers.ChoiceField(choices=ApplicationStatus.choices)


class UpdateTestApplicationStatus(BaseSerializer):
    status = serializers.ChoiceField(choices=TestApplicationStatus.choices)
