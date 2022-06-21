from django.urls import path
from rest_framework.routers import DefaultRouter

from timesheet import views

router = DefaultRouter()

router.register('time-sheet', views.TimeSheetViewSet, basename='timesheet')
router.register('check-in', views.CheckInViewSet, basename='check-in')
router.register('check-out', views.CheckOutViewSet, basename='check-out')

urlpatterns = [
    path('last-timesheet/', views.LastTimeSheet.as_view(), name='last-timesheet')
]

urlpatterns += router.urls

