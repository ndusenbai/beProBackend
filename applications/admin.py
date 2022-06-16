from django.contrib import admin

from applications.models import ApplicationToCreateCompany
from applications.actions import set_app_to_create_company_status_new


@admin.register(ApplicationToCreateCompany)
class ApplicationToCreateCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'status', 'last_name', 'first_name')
    search_fields = ('company_name', 'last_name', 'first_name')
    actions = (set_app_to_create_company_status_new, )
