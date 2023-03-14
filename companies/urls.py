from django.urls import path
from rest_framework.routers import DefaultRouter

from companies import views

router = DefaultRouter()
router.register('company', views.CompanyViewSet, basename='company')
router.register('departments', views.DepartmentViewSet, basename='department')
router.register('company-service', views.CompanyServiceViewSet, basename='company-service-viewset')
router.register('employees/timesheet', views.EmployeeTimeSheetViewSet, basename='employees-timesheet')
router.register('employees', views.EmployeesViewSet, basename='employees')
router.register('observer', views.ObserverViewSet, basename='observer-viewset')
router.register('zone', views.ZoneViewSet, basename='zone-viewset')

urlpatterns = [
    path('company-service/<int:company_id>/', views.RetrieveCompanyServiceViewSet.as_view({'get': 'retrieve'}), name='retrieve-company-service'),
] + router.urls
