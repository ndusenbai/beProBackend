from django.urls import path
from rest_framework.routers import DefaultRouter

from timesheet import views
from timesheet import tasks

router = DefaultRouter()

router.register('time-sheet', views.TimeSheetViewSet, basename='timesheet')
router.register('check-in', views.CheckInViewSet, basename='check-in')
router.register('check-out', views.CheckOutViewSet, basename='check-out')
router.register('take-time-off', views.TakeTimeOffView, basename='take-time-off')
router.register('change-timesheet', views.ChangeTimeSheetViewSet, basename='change-timesheet')
router.register('vacation', views.VacationTimeSheetViewSet, basename='vacation')

urlpatterns = [
    path('last-timesheet/', views.LastTimeSheet.as_view(), name='last-timesheet'),
    path('task-absence-check/', tasks.absence_check_request, name='task-absence-check'),
    path('create-future-timesheet/', views.CreateFutureTimeSheetAPI.as_view(), name='future-timesheet')
]

urlpatterns += router.urls

