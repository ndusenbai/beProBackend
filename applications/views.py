from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter

from applications.models import ApplicationToCreateCompany, TariffApplication, TestApplication
from applications.serializers import ApplicationToCreateCompanyModelSerializer, \
    CreateApplicationToCreateCompanySerializer, UpdateApplicationToCreateCompanySerializer, \
    TariffApplicationSerializer, TestApplicationSerializer, ApproveDeclineTariffApplication
from applications.services import approve_tariff_application, change_status_of_application_to_create_company
from utils.manual_parameters import QUERY_APPLICATIONS_STATUS
from utils.tools import log_exception


class ApplicationToCreateCompanyViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = ApplicationToCreateCompanyModelSerializer
    queryset = ApplicationToCreateCompany.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_fields = ('status',)
    search_fields = ('id', 'first_name', 'last_name', 'middle_name', 'email',
                     'phone_number', 'company_name', 'company_legal_name')
    http_method_names = ['get', 'put', 'post']

    @swagger_auto_schema(manual_parameters=[QUERY_APPLICATIONS_STATUS])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=CreateApplicationToCreateCompanySerializer)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(request_body=UpdateApplicationToCreateCompanySerializer)
    def update(self, request, *args, **kwargs):
        """
        Принятие или отклонение статуса заявки на создание компанииc. ApplicationStatus:
            NEW = 1
            ACCEPTED = 2
            DECLINED = 3
        """
        try:
            serializer = UpdateApplicationToCreateCompanySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            change_status_of_application_to_create_company(request, self.get_object(), serializer.validated_data)
            return Response({'message': 'updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, 'Error in ApplicationToCreateCompanyViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TariffApplicationView(ListModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TariffApplicationSerializer
    queryset = TariffApplication.objects.order_by()
    filterset_fields = ('status',)

    @swagger_auto_schema(manual_parameters=[QUERY_APPLICATIONS_STATUS])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TestApplicationView(ListModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TestApplicationSerializer
    queryset = TestApplication.objects.order_by()
    filterset_fields = ('status',)

    @swagger_auto_schema(manual_parameters=[QUERY_APPLICATIONS_STATUS])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ApproveTariffApplication(APIView):

    @swagger_auto_schema(request_body=ApproveDeclineTariffApplication)
    def post(self, request):
        serializer = ApproveDeclineTariffApplication(data=request.data)
        serializer.is_valid(raise_exception=True)
        approve_tariff_application(**serializer.validated_data)
        return Response({'message': 'Success'})
