from rest_framework.routers import DefaultRouter

from companies import views

router = DefaultRouter()
router.register('department-list', views.DepartmentListView, basename='department-list-view')
router.register('company', views.CompanyViewSet, basename='company')
router.register('departments', views.DepartmentViewSet, basename='department')
router.register('company-service', views.CompanyServiceViewSet, basename='company-service-viewset')
router.register('employees', views.EmployeesViewSet, basename='employees')
urlpatterns = [] + router.urls
