from django.contrib import admin

from applications.models import ApplicationToCreateCompany, TariffApplication
from applications.actions import set_status_new


@admin.register(ApplicationToCreateCompany)
class ApplicationToCreateCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'status', 'last_name', 'first_name')
    search_fields = ('company_name', 'last_name', 'first_name')
    actions = (set_status_new, )


@admin.register(TariffApplication)
class TariffApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'tariff', 'owner', 'status')
    list_display_filter = ('id', 'tariff', 'owner')
    raw_id_fields = ('tariff', 'owner')
