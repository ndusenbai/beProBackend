from rest_framework import serializers

from applications.models import ApplicationToCreateCompany, ApplicationStatus, TariffApplication, TestApplication
from utils.serializers import BaseSerializer


class TariffApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = TariffApplication
        fields = '__all__'


class TestApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestApplication
        fields = '__all__'


class ApplicationToCreateCompanyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationToCreateCompany
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['phone_number'] = data['phone_number'].replace(' ', '').replace('(', '').replace(')', '')
        return data


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


class UpdateApplicationToCreateCompanySerializer(BaseSerializer):
    status = serializers.ChoiceField(choices=ApplicationStatus.choices)


class ApproveDeclineTariffApplication(BaseSerializer):
    application_id = serializers.IntegerField()
