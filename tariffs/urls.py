from rest_framework.routers import DefaultRouter

from tariffs import views

router = DefaultRouter()

router.register('tariff', views.TariffViewSet, basename='tariff-viewset')

urlpatterns = [] + router.urls
