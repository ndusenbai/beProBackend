from django.contrib import admin

from applications.models import ApplicationToCreateCompany, TariffApplication, TestApplication
from applications.actions import set_status_new


@admin.register(ApplicationToCreateCompany)
class ApplicationToCreateCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'status', 'last_name', 'first_name')
    search_fields = ('company_name', 'last_name', 'first_name')
    actions = (set_status_new, )


@admin.register(TariffApplication)
class TariffApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'tariff', 'owner', 'start_date', 'end_date', 'status')
    raw_id_fields = ('tariff', 'owner')


@admin.register(TestApplication)
class TestApplicationAdmin(admin.ModelAdmin):
    list_display = ('test_type', 'company', 'used_quantity', 'quantity', 'status')
    search_fields = ('company__name', 'company__legal_name')
    list_filter = ('test_type', 'company')
    raw_id_fields = ('company',)
