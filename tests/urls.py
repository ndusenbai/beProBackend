from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('tests/test', views.TestViewSet, basename='test')

urlpatterns = [
    path('tests/test-one/', views.TestOneView.as_view(), name='test-one'),
    path('tests/test-two/', views.TestTwoView.as_view(), name='test-two'),
    path('tests/test-three/', views.TestThreeView.as_view(), name='test-three'),
    path('tests/test-four/', views.TestFourView.as_view(), name='test-four'),
] + router.urls
