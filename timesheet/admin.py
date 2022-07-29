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
    search_fields = ('role__user__email', 'role__user__last_name', 'role__user__first_name', 'role__user__middle_name')


@admin.register(TimeSheet)
class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'day', 'status', 'time_from', 'time_to', 'check_in', 'check_out', 'comment')
    search_fields = ('role__user__email',)
    raw_id_fields = ('role',)
    date_hierarchy = 'day'
