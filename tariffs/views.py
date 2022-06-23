from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from tariffs.models import Tariff
from tariffs.serializers import TariffModelSerializer


class TariffViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TariffModelSerializer
    queryset = Tariff.objects.order_by()
