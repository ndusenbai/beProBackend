from django.urls import path
from rest_framework.routers import DefaultRouter

from tariffs import views

router = DefaultRouter()

router.register('list-tariff', views.ListTariffViewSet, basename='list-tariff-viewset')
router.register('tariff', views.TariffViewSet, basename='tariff-viewset')

urlpatterns = [
    path('my-tariff/', views.MyTariffViewSet.as_view({'get': 'get', 'post': 'prolongate_tariff'}), name='my-tariff'),
    path('change-tariff/', views.MyTariffViewSet.as_view({'post': 'change_tariff'}), name='change-tariff'),
    path('is-tariff-over-soon/', views.IsTariffOverSoon.as_view(), name='is-tariff-over-soon'),
] + router.urls
