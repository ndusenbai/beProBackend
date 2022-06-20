from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from applications.models import ApplicationToCreateCompany, ApplicationStatus, TariffApplication, TestApplication
from applications.serializers import ApplicationToCreateCompanyModelSerializer, \
    CreateApplicationToCreateCompanySerializer, UpdateApplicationToCreateCompanySerializer, \
    TariffApplicationSerializer, TestApplicationSerializer
from applications.services import update_application_to_create_company, accept_application_to_create_company
from utils.manual_parameters import QUERY_APPLICATIONS_STATUS
from utils.tools import log_exception


class ApplicationToCreateCompanyViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = ApplicationToCreateCompanyModelSerializer
    queryset = ApplicationToCreateCompany.objects.all()
    filterset_fields = ('status',)

    @swagger_auto_schema(manual_parameters=[QUERY_APPLICATIONS_STATUS])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=CreateApplicationToCreateCompanySerializer)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(request_body=UpdateApplicationToCreateCompanySerializer)
    def update(self, request, *args, **kwargs):
        try:
            serializer = UpdateApplicationToCreateCompanySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            application_status = serializer.validated_data['status']
            if application_status == ApplicationStatus.ACCEPTED:
                accept_application_to_create_company(request, self.get_object())
            elif application_status == ApplicationStatus.DECLINED:
                update_application_to_create_company(self.get_object(), {'status': application_status})
            else:
                return Response({'message': 'Incorrect status'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

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
