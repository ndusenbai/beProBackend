from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from applications.models import TariffApplication
from tariffs.models import Tariff, TestPrice
from tariffs.serializers import TariffModelSerializer, UpdateTariffSerializer, MyTariffSerializer, ChangeTariff, \
    TestPriceModelSerializer
from tariffs.services import update_tariff_application, delete_tariff, get_my_tariff, prolongate_my_tariff, \
    change_my_tariff, deactivate_my_tariff, check_if_tariff_over_soon, get_test_prices, update_test_price
from utils.permissions import IsSuperuser, IsOwnerOrSuperuser, IsStaffPermission
from utils.tools import log_exception


class ListTariffViewSet(ListModelMixin, GenericViewSet):
    serializer_class = TariffModelSerializer
    queryset = Tariff.objects.filter(is_active=True)


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


class TestPriceViewSet(GenericViewSet):
    permission_classes = (IsStaffPermission,)
    serializer_class = TestPriceModelSerializer
    queryset = TestPrice.objects.all()
    pagination_class = None

    def get(self, request):
        return Response(get_test_prices())

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_test_price(**serializer.validated_data)
        return Response({'message': 'updated'})


class MyTariffViewSet(GenericViewSet):
    permission_classes = (IsOwnerOrSuperuser,)
    queryset = TariffApplication.objects.order_by()
    serializer_class = MyTariffSerializer
    pagination_class = None

    @swagger_auto_schema(responses={200: MyTariffSerializer()})
    def get(self, request):
        response, status_code = get_my_tariff(request.user)
        return Response(response, status_code)

    def prolongate_tariff(self, request):
        response, status_code = prolongate_my_tariff(request.user)
        return Response(response, status_code)

    @swagger_auto_schema(request_body=ChangeTariff)
    def change_tariff(self, request):
        """
        Поменять тариф. period: 1=MONTHLY, 2=YEARLY
        """
        serializer = ChangeTariff(data=request.data)
        serializer.is_valid(raise_exception=True)
        response, status_code = change_my_tariff(request.user, **serializer.validated_data)
        return Response(response, status_code)

    def deactivate_tariff(self, request):
        deactivate_my_tariff(request.user)
        return Response({'message': 'success'})


class IsTariffOverSoon(APIView):
    permission_classes = (IsOwnerOrSuperuser,)

    def get(self, request):
        return Response({'tariff_is_over_soon': check_if_tariff_over_soon(request.user)})
