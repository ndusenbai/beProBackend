from django.contrib import admin
from .models import EmployeeNotification, TestNotification



class EmployeeNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'check_in_notified', 'check_out_notified', 'created_at')


class TestNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role_id', 'title')

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)


admin.site.register(EmployeeNotification, EmployeeNotificationAdmin)
admin.site.register(TestNotification)
