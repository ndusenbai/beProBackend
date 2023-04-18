from django.contrib import admin
from .models import EmployeeNotification


class EmployeeNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'check_in_notified', 'check_out_notified', 'created_at')


admin.site.register(EmployeeNotification, EmployeeNotificationAdmin)
