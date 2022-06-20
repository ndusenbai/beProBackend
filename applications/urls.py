from rest_framework.routers import DefaultRouter

from applications import views

router = DefaultRouter()

router.register('test-application', views.TestApplicationView, basename='test-application-view')
router.register('tariff-application', views.TariffApplicationView, basename='tariff-application-view')
router.register('to-create-company', views.ApplicationToCreateCompanyViewSet, basename='to-create-company')

urlpatterns = [] + router.urls
