from rest_framework.routers import DefaultRouter
from django.urls import path
from bepro_statistics.views import StatisticViewSet, UserStatisticViewSet, UserStatisticAPI

router = DefaultRouter()

router.register('user-statistic', UserStatisticViewSet, basename='user-statistic-viewset')
router.register('statistic', StatisticViewSet, basename='statistic-viewset')

urlpatterns = [
    path('user-all-stats/', UserStatisticAPI.as_view())
]

urlpatterns += router.urls

