from django.contrib import admin
from companies.models import Company, Department, Role, CompanyService


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'owner', 'is_deleted', 'max_employees_qty', 'is_active')
    search_fields = ('name', 'legal_name', 'owner__first_name', 'owner__last_name')
    raw_id_fields = ('owner',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',  'id', 'company', 'company_id')
    search_fields = ('name', 'company__name', 'company__legal_name')
    raw_id_fields = ('company', 'head_of_department')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('company', 'company_id', 'department', 'department_id', 'get_user_email', 'role', 'title', 'grade')
    search_fields = ('company', 'department', 'role')
    list_filter = ('company', 'role')
    raw_id_fields = ('company', 'department', 'user')

    @admin.display(ordering='user__email', description='User email')
    def get_user_email(self, obj):
        return obj.user.email


@admin.register(CompanyService)
class CompanyServiceAdmin(admin.ModelAdmin):
    list_display = ('company', 'analytics_enabled', 'time_tracking_enabled', 'tests_enabled')
    list_display_links = ('company',)
