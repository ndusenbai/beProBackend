from django.urls import path
from rest_framework.routers import DefaultRouter

from tariffs import views

router = DefaultRouter()

router.register('tariff', views.TariffViewSet, basename='tariff-viewset')

urlpatterns = [
    path('my-tariff/', views.MyTariffViewSet.as_view({'get': 'get'}), name='my-tariff'),
] + router.urls
