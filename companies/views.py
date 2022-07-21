from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from rest_framework.filters import SearchFilter

from companies.models import CompanyService
from companies.serializers import CompanyModelSerializer, DepartmentSerializer, DepartmentListSerializer, \
    DepartmentList2Serializer, CompanySerializer, CompanyServiceSerializer, EmployeesSerializer, \
    CreateEmployeeSerializer, UpdateDepartmentSerializer, FilterEmployeesSerializer
from companies.services import update_department, get_department_list, create_company, create_department, \
    get_departments_qs, get_company_qs, update_company, get_employee_list, create_employee, update_employee, \
    delete_head_of_department_role
from utils.manual_parameters import QUERY_COMPANY, QUERY_DEPARTMENTS
from utils.tools import log_exception

User = get_user_model()


class CompanyServiceViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyServiceSerializer
    queryset = CompanyService.objects.order_by()


class CompanyViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('name', 'legal_name')
    filterset_fields = ('owner',)
    http_method_names = ['get', 'post', 'put', 'delete']

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

    def perform_destroy(self, instance):
        update_company(instance, {'is_deleted': True})


class DepartmentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_fields = ('company',)
    search_fields = ('name',)
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return DepartmentSerializer
        elif self.action == 'update':
            return UpdateDepartmentSerializer
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

    def perform_destroy(self, instance):
        delete_head_of_department_role(instance)
        super().perform_destroy(instance)


class DepartmentListView(ListModelMixin, GenericViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentListSerializer

    def get_queryset(self):
        return get_department_list(self.request.user.selected_company)


class EmployeesViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeesSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name')
    filterset_fields = ('company', 'department')
    http_method_names = ['get', 'post', 'put', 'delete']
    filter_serializer = None

    def get_queryset(self):
        return get_employee_list()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if self.filter_serializer:
            data = self.filter_serializer.validated_data
            if 'departments' in data:
                return queryset.filter(department__in=data['departments'])
        return queryset

    @swagger_auto_schema(manual_parameters=[QUERY_DEPARTMENTS])
    def list(self, request, *args, **kwargs):
        self.filter_serializer = FilterEmployeesSerializer(data=request.query_params)
        self.filter_serializer.is_valid(raise_exception=True)
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=CreateEmployeeSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateEmployeeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            create_employee(serializer.validated_data)
            return Response({'message': 'created'})
        except Exception as e:
            log_exception(e, 'Error in EmployeesViewSet.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=CreateEmployeeSerializer)
    def update(self, request, *args, **kwargs):
        try:
            serializer = CreateEmployeeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            update_employee(self.get_object(), serializer.validated_data)
            return Response({'message': 'updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, 'Error in DepartmentViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
