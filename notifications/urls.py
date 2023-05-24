from django.urls import path

from notifications.views import NotificationHandler, TestNotificationAPI

urlpatterns = [
    path('check/', NotificationHandler.as_view(), name='notification-cron'),
    path('test-notifications/', TestNotificationAPI.as_view())
]

