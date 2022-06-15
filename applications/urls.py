from rest_framework.routers import DefaultRouter

from applications import views

router = DefaultRouter()

router.register('to-create-company', views.ApplicationToCreateCompanyViewSet, basename='to-create-company')

urlpatterns = [] + router.urls
