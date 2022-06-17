from rest_framework.routers import DefaultRouter

from bepro_statistics.views import StatisticViewSet

router = DefaultRouter()

router.register(r'statistic', StatisticViewSet, basename='statistic-viewset')

urlpatterns = [

]

urlpatterns += router.urls

