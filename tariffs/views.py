from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from tariffs.models import Tariff
from tariffs.serializers import TariffModelSerializer, UpdateTariffSerializer
from tariffs.services import update_tariff_application
from utils.tools import log_exception


class TariffViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TariffModelSerializer
    queryset = Tariff.objects.order_by()

    @swagger_auto_schema(request_body=UpdateTariffSerializer)
    def update(self, request, *args, **kwargs):
        try:
            serializer = UpdateTariffSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            update_tariff_application(self.get_object(), serializer.validated_data)
            return Response({'message': 'updated'})
        except Exception as e:
            log_exception(e, 'Error in TariffViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
