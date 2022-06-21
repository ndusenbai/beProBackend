from django.contrib import admin

from timesheet.models import EmployeeSchedule, DepartmentSchedule, TimeSheet


@admin.register(DepartmentSchedule)
class DepartmentScheduleAdmin(admin.ModelAdmin):
    list_display = ('department', 'week_day', 'time_from', 'time_to')
    search_fields = ('department',)


@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'week_day', 'time_from', 'time_to')
    raw_id_fields = ('user', 'company')
    search_fields = ('user',)


@admin.register(TimeSheet)
class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'day', 'status', 'time_from', 'time_to', 'check_in', 'check_out', 'comment')
    search_fields = ('user', 'company')
    list_filter = ('company',)
    raw_id_fields = ('user', 'company')
