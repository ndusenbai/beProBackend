from rest_framework.routers import DefaultRouter
from scores import views

router = DefaultRouter()

router.register('reason', views.ReasonViewSet, basename='reason-viewset')
# router.register('score-feed', views.ScoreFeedListView, basename='score-feed-view')
router.register('score', views.ScoreViewSet, basename='score-viewset')
router.register('month-scores', views.MonthScoresViewSet, basename='month-scores')

urlpatterns = [

]

urlpatterns += router.urls
