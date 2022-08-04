from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from applications.models import TariffApplication
from tariffs.models import Tariff
from tariffs.serializers import TariffModelSerializer, UpdateTariffSerializer, MyTariffSerializer
from tariffs.services import update_tariff_application, delete_tariff, get_my_tariff
from utils.permissions import IsSuperuser, IsOwnerOrSuperuser
from utils.tools import log_exception


class TariffViewSet(ModelViewSet):
    permission_classes = (IsSuperuser,)
    serializer_class = TariffModelSerializer
    queryset = Tariff.objects.filter(is_active=True)

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

    def perform_destroy(self, instance):
        delete_tariff(instance)


class MyTariffViewSet(GenericViewSet):
    permission_classes = (IsOwnerOrSuperuser,)
    queryset = TariffApplication.objects.order_by()
    serializer_class = MyTariffSerializer
    pagination_class = None

    def get(self, request):
        response, status_code = get_my_tariff(request.user)
        return Response(response, status_code)
