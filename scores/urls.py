from rest_framework.routers import DefaultRouter
from scores.views import ReasonViewSet, ScoreViewSet

router = DefaultRouter()

router.register(r'reason', ReasonViewSet, basename='reason-viewset')
router.register(r'score', ScoreViewSet, basename='score-viewset')


urlpatterns = [

]

urlpatterns += router.urls
