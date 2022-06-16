from rest_framework.routers import DefaultRouter

from companies import views

router = DefaultRouter()

router.register('company', views.CompanyViewSet, basename='company')
router.register('department', views.DepartmentViewSet, basename='department')
router.register('department-schedule', views.DepartmentScheduleViewSet, basename='department-schedule')
router.register('employee-schedule', views.EmployeeScheduleViewSet, basename='employee-schedule')

urlpatterns = [] + router.urls
