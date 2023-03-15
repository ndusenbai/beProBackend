from rest_framework.routers import DefaultRouter
from django.urls import path
from bepro_statistics import views

router = DefaultRouter()

router.register('user-statistic', views.UserStatisticViewSet, basename='user-statistic-viewset')
router.register('statistic', views.StatisticViewSet, basename='statistic-viewset')
router.register('stats-for-user', views.StatsForUser, basename='stats-for-user')
router.register('history-stats-for-user', views.HistoryStats, basename='history-stats')
router.register('create-user-stat', views.CreateUserStat, basename='create-user-stat')
router.register('change-user-stat', views.ChangeUserStat, basename='change-user-stat')

urlpatterns = [
    path('pdf/generate-stat/', views.GenerateStatPdfViewSet.as_view(), name='generate-stat-pdf'),
    path('pdf/generate-history-stat/', views.GenerateHistoryStatPdfViewSet.as_view(), name='generate-history-stat-pdf'),
    path('pdf/generate-dynamic-stat/', views.GenerateDynamicStatPdfViewSet.as_view(), name='generate-dynamic-stat-pdf'),
]

urlpatterns += router.urls

