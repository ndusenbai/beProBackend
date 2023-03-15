from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView
from companies.models import CompanyService
from companies.serializers import CompanyModelSerializer, DepartmentSerializer, \
    DepartmentList2Serializer, CompanySerializer, CompanyServiceSerializer, EmployeesSerializer, \
    CreateEmployeeSerializer, UpdateDepartmentSerializer, FilterEmployeesSerializer, ObserverListSerializer, \
    ObserverCreateSerializer, ObserverUpdateSerializer, CompanyServicesUpdateSerializer, \
    RetrieveCompanyServiceSerializer, CompanyUpdateModelSerializer, ZoneCreateSerializer, ZoneListSerializer, \
    EmployeeTimeSheetSerializer, GenerateEmployeeTimeSheetSerializer
from companies.services import update_department, create_company, create_department, \
    get_departments_qs, get_company_qs, update_company, get_employee_list, create_employee, update_employee, \
    delete_head_of_department_role, update_observer, create_observer_and_role, get_observers_qs, \
    update_company_services, get_qs_retrieve_company_services, get_zones_qs, get_employee_time_sheet, \
    generate_employees_timesheet_excel
from utils.manual_parameters import QUERY_COMPANY, QUERY_DEPARTMENTS
from utils.permissions import CompanyPermissions, DepartamentPermissions, EmployeesPermissions, ObserverPermission, \
    SuperuserOrOwnerOrHRPermission
from utils.tools import log_exception

User = get_user_model()


class CompanyServiceViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = (SuperuserOrOwnerOrHRPermission,)
    serializer_class = CompanyServiceSerializer

    def get_queryset(self):
        return CompanyService.objects.filter(
            company__owner=self.request.user,
            company__is_deleted=False,
        )

    @swagger_auto_schema(request_body=CompanyServicesUpdateSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = CompanyServicesUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            update_company_services(serializer.validated_data)
            return Response({'message': 'updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, 'Error in CompanyServiceViewSet.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RetrieveCompanyServiceViewSet(RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RetrieveCompanyServiceSerializer

    def get_queryset(self):
        return get_qs_retrieve_company_services()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.kwargs['company_id'])
        self.check_object_permissions(self.request, obj)
        return obj


class CompanyViewSet(ModelViewSet):
    permission_classes = (CompanyPermissions,)
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
        elif self.action in ['update', 'partial_update']:
            return CompanyUpdateModelSerializer
        return CompanyModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_company(request.user, serializer.validated_data)
        return Response({'message': 'created'})

    def perform_destroy(self, instance):
        if instance.is_main:
            raise PermissionDenied
        update_company(instance, {'is_deleted': True})


class DepartmentViewSet(ModelViewSet):
    permission_classes = (DepartamentPermissions,)
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
        try:
            create_department(request.user, serializer.validated_data)
        except Exception as e:
            if type(e.args[0]) == dict and e.args[0]['status'] == 400:
                return Response({'message': e.args[0]['message']}, status=e.args[0]['status'])
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        if instance.is_hr:
            raise PermissionDenied()
        delete_head_of_department_role(instance)
        super().perform_destroy(instance)


class EmployeesViewSet(ModelViewSet):
    permission_classes = (EmployeesPermissions,)
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
        except ValidationError as e:
            return Response(e.detail, status.HTTP_400_BAD_REQUEST)
        except Exception as e:

            if type(e.args[0]) == dict and e.args[0]['status'] == 400:
                return Response({'message': e.args[0]['message']}, status=e.args[0]['status'])

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


class EmployeeTimeSheetViewSet(ModelViewSet):
    http_method_names = ['get']
    permission_classes = (EmployeesPermissions,)
    serializer_class = EmployeeTimeSheetSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name')
    filterset_fields = ('company', 'department')
    filter_serializer = None

    def get_queryset(self):
        return get_employee_time_sheet()

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


class ObserverViewSet(ModelViewSet):
    permission_classes = (ObserverPermission,)
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return ObserverCreateSerializer
        elif self.action == 'update':
            return ObserverUpdateSerializer

        return ObserverListSerializer

    def get_queryset(self):
        return get_observers_qs(self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            response, status_code = create_observer_and_role(serializer.validated_data)
            return Response(response, status=status_code)
        except Exception as e:
            if type(e.args[0]) == dict and e.args[0]['status'] == 400:
                return Response({'message': e.args[0]['message']}, status=e.args[0]['status'])

            log_exception(e, 'Error in ObserverViewSet.create()')
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_observer(self.get_object(), serializer.validated_data)
        return Response({'message': 'updated'})


class ZoneViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('address',)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.role.company)

    def get_queryset(self):
        return get_zones_qs(self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ZoneListSerializer
        return ZoneCreateSerializer


class GenerateEmployeeTimeSheetAPI(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=GenerateEmployeeTimeSheetSerializer)
    def post(self, request):
        serializer = GenerateEmployeeTimeSheetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return generate_employees_timesheet_excel(
            serializer.validated_data['company'],
            None
        )
