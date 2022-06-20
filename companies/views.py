from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from companies.models import Company, Department, EmployeeSchedule
from companies.serializers import CompanyModelSerializer, DepartmentSerializer, UpdateEmployeeScheduleSerializer,\
    ScheduleSerializer
from companies.services import update_department
from utils.manual_parameters import QUERY_USER, QUERY_COMPANY
from utils.tools import log_exception

User = get_user_model()


class CompanyViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyModelSerializer
    queryset = Company.objects.order_by()


class DepartmentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentSerializer
    queryset = Department.objects.order_by()
    filterset_fields = ('company',)

    def get_queryset(self):
        return Department.objects.prefetch_related(Prefetch('department_schedules', to_attr='schedules'))

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
