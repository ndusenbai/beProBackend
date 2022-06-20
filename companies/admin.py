from django.contrib import admin
from companies.models import Company, Department, DepartmentSchedule, EmployeeSchedule, Role


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'is_active')
    search_fields = ('name', 'legal_name')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company__name', 'company__legal_name')


@admin.register(DepartmentSchedule)
class DepartmentScheduleAdmin(admin.ModelAdmin):
    list_display = ('department', 'week_day', 'time_from', 'time_to')
    search_fields = ('department',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('company', 'department', 'user', 'role', 'title', 'grade')
    search_fields = ('company', 'department', 'role')
    list_filter = ('company', 'role')
    raw_id_fields = ('company', 'department', 'user')


@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'week_day', 'time_from', 'time_to')
    search_fields = ('user',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'company', 'department')
    list_display_links = ('id', 'user')


