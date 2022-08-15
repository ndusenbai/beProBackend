from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

urlpatterns = [
    path('tests/test-four/', views.TestFourView.as_view(), name='test-four'),
    path('tests/test-two/', views.TestTwoView.as_view(), name='test-two'),
] + router.urls
