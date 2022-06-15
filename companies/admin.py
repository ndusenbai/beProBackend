from django.contrib import admin
from companies.models import Company, Department, Schedule


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'is_active')
    search_fields = ('name', 'legal_name')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company__name', 'company__legal_name')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('department', 'week_day', 'time_from', 'time_to')
    search_fields = ('department',)
