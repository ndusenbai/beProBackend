from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from companies.models import Company, Department, Schedule
from companies.serializers import CompanyModelSerializer, DepartmentModelSerializer, ScheduleModelSerializer, \
    UpdateScheduleSerializer
from companies.services import update_schedule


class CompanyViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyModelSerializer
    queryset = Company.objects.order_by()


class DepartmentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentModelSerializer
    queryset = Department.objects.order_by()


class ScheduleViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ScheduleModelSerializer
    queryset = Schedule.objects.order_by()
    filterset_fields = ('department',)

    @swagger_auto_schema(request_body=UpdateScheduleSerializer)
    def update(self, request, *args, **kwargs):
        serializer = UpdateScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_schedule(self.get_object(), **serializer.validated_data)
        return Response({'message': 'updated'}, status=status.HTTP_200_OK)
