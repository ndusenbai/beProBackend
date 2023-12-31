from django.contrib import admin
from .models import EmployeeNotification, TestNotification
from firebase_admin.messaging import Message, Notification, APNSConfig, APNSPayload, Aps
from fcm_django.models import FCMDevice
from django.apps import apps


@admin.action(description='Send push notifications')
def send_push_notification(modeladmin, request, queryset):
    for push_notification in queryset:
        role = apps.get_model(app_label='companies', model_name='Role').objects.get(id=push_notification.role_id)
        devices = FCMDevice.objects.filter(user=role.user)

        devices.send_message(

            Message(
                apns=APNSConfig(payload=APNSPayload(aps=Aps(mutable_content=True))),
                notification=Notification(
                    title=push_notification.title,
                    body=push_notification.body
                )
            )
        )


class EmployeeNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'check_in_notified', 'check_out_notified', 'created_at')


class TestNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role_id', 'title')

    actions = [send_push_notification]


admin.site.register(EmployeeNotification, EmployeeNotificationAdmin)
admin.site.register(TestNotification, TestNotificationAdmin)
