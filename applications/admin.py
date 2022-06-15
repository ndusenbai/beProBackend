from django.contrib import admin
from applications.models import ApplicationToCreateCompany


@admin.register(ApplicationToCreateCompany)
class ApplicationToCreateCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'last_name', 'first_name')
    search_fields = ('company_name', 'last_name', 'first_name')
