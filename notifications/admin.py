from django.contrib import admin
from .models import EmployeeNotification, TestNotification
from django.apps import apps
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice


class EmployeeNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'check_in_notified', 'check_out_notified', 'created_at')


class TestNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role_id', 'title')

    def save_model(self, request, obj, form, change):
        role = apps.get_model(app_label='companies', model_name='Role').objects.filter(id=self.role_id)
        devices = FCMDevice.objects.filter(user_id=role.user.id)
        devices.send_message(Message(notification=Notification(title=self.title, body=self.body)))
        super().save_model(request, obj, form, change)


admin.site.register(EmployeeNotification, EmployeeNotificationAdmin)
admin.site.register(TestNotification)
