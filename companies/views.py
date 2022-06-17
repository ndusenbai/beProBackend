from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from companies.models import Company, Department, DepartmentSchedule, EmployeeSchedule
from companies.serializers import CompanyModelSerializer, DepartmentModelSerializer, DepartmentScheduleModelSerializer, \
    UpdateDepartmentScheduleSerializer, EmployeeScheduleModelSerializer, UpdateEmployeeScheduleSerializer, \
    DepartmentListSerializer
from companies.services import update_department_schedule, update_employee_schedule, get_department_list


class CompanyViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyModelSerializer
    queryset = Company.objects.order_by()


class DepartmentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentModelSerializer
    queryset = Department.objects.order_by()


class DepartmentScheduleViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentScheduleModelSerializer
    queryset = DepartmentSchedule.objects.order_by()
    filterset_fields = ('department',)

    @swagger_auto_schema(request_body=UpdateDepartmentScheduleSerializer)
    def update(self, request, *args, **kwargs):
        serializer = UpdateDepartmentScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_department_schedule(self.get_object(), **serializer.validated_data)
        return Response({'message': 'updated'}, status=status.HTTP_200_OK)


class EmployeeScheduleViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeeScheduleModelSerializer
    queryset = EmployeeSchedule.objects.order_by()
    filterset_fields = ('user',)

    @swagger_auto_schema(request_body=UpdateEmployeeScheduleSerializer)
    def update(self, request, *args, **kwargs):
        serializer = UpdateEmployeeScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_employee_schedule(self.get_object(), **serializer.validated_data)
        return Response({'message': 'updated'}, status=status.HTTP_200_OK)


class DepartmentListView(ListModelMixin, GenericViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentListSerializer

    def get_queryset(self):
        return get_department_list(self.request.user.selected_company)
