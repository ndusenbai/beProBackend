from django.contrib import admin

from timesheet.models import EmployeeSchedule, DepartmentSchedule, TimeSheet


@admin.register(DepartmentSchedule)
class DepartmentScheduleAdmin(admin.ModelAdmin):
    list_display = ('department', 'week_day', 'time_from', 'time_to')
    search_fields = ('department',)


@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(admin.ModelAdmin):
    list_display = ('role', 'week_day', 'time_from', 'time_to')
    raw_id_fields = ('role',)
    search_fields = ('role',)


@admin.register(TimeSheet)
class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('role', 'day', 'status', 'time_from', 'time_to', 'check_in', 'check_out', 'comment')
    search_fields = ('role',)
    raw_id_fields = ('role',)
    date_hierarchy = 'day'
