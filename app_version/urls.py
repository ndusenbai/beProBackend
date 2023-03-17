from django.urls import path
from .views import AppVersionAPI

urlpatterns = [
    path('app-version/', AppVersionAPI.as_view())
]
