from rest_framework.routers import DefaultRouter

from companies import views

router = DefaultRouter()
router.register('company', views.CompanyViewSet, basename='company')
router.register('departments', views.DepartmentViewSet, basename='department')
router.register('employees', views.EmployeesViewSet, basename='employees')
router.register('observer', views.ObserverViewSet, basename='observer-viewset')
urlpatterns = [] + router.urls
