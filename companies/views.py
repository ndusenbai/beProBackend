from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin

from companies.models import Company, Department, CompanyService
from companies.serializers import CompanyModelSerializer, DepartmentSerializer, DepartmentListSerializer, \
    DepartmentList2Serializer, CompanySerializer, CompanyServiceSerializer
from companies.services import update_department, get_department_list, create_company, create_department, \
    get_departments_qs, get_company_qs
from utils.manual_parameters import QUERY_COMPANY
from utils.tools import log_exception

User = get_user_model()


class CompanyServiceViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyServiceSerializer
    queryset = CompanyService.objects.order_by()


class CompanyViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyModelSerializer
    filterset_fields = ('owner',)

    def get_queryset(self):
        return get_company_qs()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CompanySerializer
        return CompanyModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_company(request.user, serializer.validated_data)
        return Response({'message': 'created'})


class DepartmentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('company',)

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return DepartmentSerializer
        return DepartmentList2Serializer

    def get_queryset(self):
        return get_departments_qs()

    @swagger_auto_schema(request_body=DepartmentSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_department(request.user, serializer.validated_data)
        return Response({'message': 'created'})

    @swagger_auto_schema(manual_parameters=[QUERY_COMPANY])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            update_department(self.get_object(), serializer.validated_data)
            return Response({'message': 'updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, 'Error in DepartmentViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartmentListView(ListModelMixin, GenericViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentListSerializer

    def get_queryset(self):
        return get_department_list(self.request.user.selected_company)
