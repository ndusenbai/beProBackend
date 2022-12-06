from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from applications.models import ApplicationToCreateCompany, TariffApplication, TestApplication
from applications.serializers import ApplicationToCreateCompanyModelSerializer, \
    CreateApplicationToCreateCompanySerializer, UpdateApplicationStatusSerializer, \
    TariffApplicationSerializer, TestApplicationModelSerializer, TariffApplicationRetrieveSerializer, \
    CreateTestApplicationSerializer, ListTestApplicationsSerializer
from applications.services import change_status_of_application_to_create_company, change_status_of_tariff_application, \
    change_status_of_test_application
from auth_user.utils import UserAlreadyExists
from companies.utils import CompanyAlreadyExists
from utils.manual_parameters import QUERY_APPLICATIONS_STATUS, QUERY_TEST_APPLICATIONS_STATUS, \
    QUERY_APPLICATIONS_STATUSES
from utils.permissions import IsAssistantMarketingOrSuperuser, TestApplicationPermission, TariffApplicationPermission, \
    SuperuserOrOwnerOrHRorHeadOfHRDepartmentPermission
from utils.tools import log_exception


class ApplicationToCreateCompanyViewSet(ListModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = (IsAssistantMarketingOrSuperuser, )
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

    @swagger_auto_schema(request_body=UpdateApplicationStatusSerializer)
    def update(self, request, *args, **kwargs):
        """
        Принятие или отклонение статуса заявки на создание компании. ApplicationStatus:
            NEW = 1
            ACCEPTED = 2
            DECLINED = 3
        """
        try:
            serializer = UpdateApplicationStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            change_status_of_application_to_create_company(request, self.get_object(), serializer.validated_data)
            return Response({'message': 'updated'}, status=status.HTTP_200_OK)
        except CompanyAlreadyExists as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except UserAlreadyExists as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except Exception as e:
            log_exception(e, 'Error in ApplicationToCreateCompanyViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApplicationToCreateCompanyCreateViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (AllowAny, )
    serializer_class = ApplicationToCreateCompanyModelSerializer
    queryset = ApplicationToCreateCompany.objects.all()

    @swagger_auto_schema(request_body=CreateApplicationToCreateCompanySerializer)
    def create(self, request, *args, **kwargs):
        """
        Создание заявки на создание компании. TariffPeriod:1 = MONTHLY, 2 = YEARLY
        """
        return super().create(request, *args, **kwargs)


class TariffApplicationView(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (TariffApplicationPermission,)
    queryset = TariffApplication.objects.order_by('-created_at')
    filterset_fields = ('owner',)
    http_method_names = ['get', 'put']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TariffApplicationRetrieveSerializer
        return TariffApplicationSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        filters = self.request.query_params
        if 'status' in filters:
            if ',' in filters['status']:
                statuses = [int(i) for i in filters['status'].split(',')]
                return queryset.filter(status__in=statuses)
            return queryset.filter(status=filters['status'])
        return queryset

    @swagger_auto_schema(manual_parameters=[QUERY_APPLICATIONS_STATUSES])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=UpdateApplicationStatusSerializer)
    def update(self, request, *args, **kwargs):
        """
        Принятие или отклонение статуса заявки на продление. ApplicationStatus:
            NEW = 1
            ACCEPTED = 2
            DECLINED = 3
        """
        try:
            serializer = UpdateApplicationStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            change_status_of_tariff_application(self.get_object(), serializer.validated_data['status'])
            return Response({'message': 'updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, 'Error in TariffApplicationView.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateTestApplicationView(CreateModelMixin, GenericViewSet):
    permission_classes = (SuperuserOrOwnerOrHRorHeadOfHRDepartmentPermission,)
    queryset = TestApplication.objects.all()
    serializer_class = TestApplicationModelSerializer

    @swagger_auto_schema(request_body=CreateTestApplicationSerializer)
    def create(self, request, *args, **kwargs):
        """
        Типы тестов. TestType:
            ONE_HEART_PRO = 1
            TWO_BRAIN = 2
            THREE_BRAIN_PRO = 3
            FOUR_HEART = 4
        """
        return super().create(request, *args, **kwargs)


class TestApplicationView(ListModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (TestApplicationPermission,)
    queryset = TestApplication.objects.all()
    serializer_class = TestApplicationModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('company__owner__first_name', 'company__owner__last_name', 'created_at')
    filterset_fields = ('company',)
    http_method_names = ['get', 'put']
    filter_serializer = None

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if self.filter_serializer:
            data = self.filter_serializer.validated_data
            if 'status' in data:
                return queryset.filter(status__in=data['status'])
        return queryset

    @swagger_auto_schema(manual_parameters=[QUERY_TEST_APPLICATIONS_STATUS])
    def list(self, request, *args, **kwargs):
        self.filter_serializer = ListTestApplicationsSerializer(data=request.query_params)
        self.filter_serializer.is_valid(raise_exception=True)
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=UpdateApplicationStatusSerializer)
    def update(self, request, *args, **kwargs):
        """
        Принятие или отклонение статуса заявки на тест. TestApplicationStatus:
            NEW = 1
            ACCEPTED = 2
            DECLINED = 3
            USED = 4
        """
        try:
            serializer = UpdateApplicationStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            change_status_of_test_application(self.get_object(), serializer.validated_data['status'])
            return Response({'message': 'updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, 'Error in TestApplicationView.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

