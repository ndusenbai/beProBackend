from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from timesheet.models import TimeSheet
from timesheet.serializers import CheckInSerializer, CheckOutSerializer, TimeSheetModelSerializer, \
    TimeSheetListSerializer, TimeSheetUpdateSerializer
from timesheet.services import create_check_in_timesheet, get_last_timesheet_action, create_check_out_timesheet, \
    get_timesheet_qs_by_month, update_timesheet
from timesheet.utils import EmployeeTooFarFromDepartment, FillUserStatistic
from utils.manual_parameters import QUERY_YEAR, QUERY_MONTH, QUERY_ROLE
from utils.tools import log_exception


User = get_user_model()


class TimeSheetViewSet(ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = TimeSheetModelSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            serializer = TimeSheetListSerializer(data=self.request.query_params)
            serializer.is_valid(raise_exception=True)
            qs = get_timesheet_qs_by_month(serializer.validated_data)
            return qs
        return TimeSheet.objects.all()

    @swagger_auto_schema(manual_parameters=[QUERY_ROLE, QUERY_MONTH, QUERY_YEAR])
    def list(self, request, *args, **kwargs):
        """
        Получить расписание за определенный месяц на роль
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=TimeSheetUpdateSerializer)
    def update(self, request, *args, **kwargs):
        try:
            serializer = TimeSheetUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            update_timesheet(self.get_object(), serializer.validated_data)
            return Response({'message': 'updated'})
        except Exception as e:
            log_exception(e, 'Error in TimeSheetViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class LastTimeSheet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        last_action = get_last_timesheet_action(request.user.role)
        return Response({'last_action': last_action})


class CheckInViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=CheckInSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = CheckInSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            create_check_in_timesheet(request.user.role, serializer.validated_data)
            return Response({'message': 'created'})
        except EmployeeTooFarFromDepartment as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except Exception as e:
            log_exception(e, 'Error in CheckInViewSet.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckOutViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=CheckOutSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = CheckOutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            result = create_check_out_timesheet(request.user.role, serializer.validated_data)
            if not result:
                Response({'message': 'check_in_again'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'message': 'created'})
        except FillUserStatistic as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except Exception as e:
            log_exception(e, 'Error in CheckInViewSet.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
