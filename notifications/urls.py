from django.urls import path

from notifications.views import NotificationHandler

urlpatterns = [
    path('check/', NotificationHandler.as_view(), name='notification-cron'),
]

