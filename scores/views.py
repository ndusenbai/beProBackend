from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from scores.serializers import ReasonSerializer, ScoreSerializer
from scores.models import Reason, Score


class ReasonViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReasonSerializer
    queryset = Reason.objects.order_by()


class ScoreViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ScoreSerializer
    queryset = Score.objects.order_by()

