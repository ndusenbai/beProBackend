from rest_framework.routers import DefaultRouter

from companies import views

router = DefaultRouter()

router.register('company', views.CompanyViewSet, basename='company')
router.register('department', views.DepartmentViewSet, basename='department')
router.register('schedule', views.ScheduleViewSet, basename='schedule')

urlpatterns = [] + router.urls
