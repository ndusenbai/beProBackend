from rest_framework.routers import DefaultRouter
from django.urls import path
from bepro_statistics import views

router = DefaultRouter()

router.register('user-statistic', views.UserStatisticViewSet, basename='user-statistic-viewset')
router.register('statistic', views.StatisticViewSet, basename='statistic-viewset')
router.register('stats-for-user', views.StatsForUser, basename='stats-for-user')
router.register('create-user-stat', views.CreateUserStat, basename='create-user-stat')

urlpatterns = [
    path('user-all-stats/', views.UserStatisticAPI.as_view())
]

urlpatterns += router.urls

