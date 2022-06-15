from rest_framework import serializers

from applications.models import ApplicationToCreateCompany, ApplicationStatus
from utils.serializers import BaseSerializer


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
    employees_qty = serializers.IntegerField(default=0)
    years_of_work = serializers.IntegerField(default=0)


class UpdateApplicationToCreateCompanySerializer(BaseSerializer):
    status = serializers.ChoiceField(choices=ApplicationStatus.choices)
