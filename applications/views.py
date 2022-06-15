from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from applications.models import ApplicationToCreateCompany, ApplicationStatus
from applications.serializers import ApplicationToCreateCompanyModelSerializer, \
    CreateApplicationToCreateCompanySerializer, UpdateApplicationToCreateCompanySerializer
from applications.services import update_application_to_create_company, accept_application_to_create_company
from utils.manual_parameters import QUERY_APPLICATIONS_STATUS


class ApplicationToCreateCompanyViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = ApplicationToCreateCompanyModelSerializer
    queryset = ApplicationToCreateCompany.objects.all()
    filterset_fields = ('status',)

    @swagger_auto_schema(manual_parameters=[QUERY_APPLICATIONS_STATUS])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=CreateApplicationToCreateCompanySerializer())
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(request_body=UpdateApplicationToCreateCompanySerializer)
    def update(self, request, *args, **kwargs):
        serializer = UpdateApplicationToCreateCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application_status = serializer.validated_data['status']
        if application_status == ApplicationStatus.ACCEPTED:
            accept_application_to_create_company(self.get_object())
        elif application_status == ApplicationStatus.DECLINED:
            update_application_to_create_company(self.get_object(), {'status': application_status})
        else:
            return Response({'message': 'Incorrect status'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'updated'}, status=status.HTTP_200_OK)
