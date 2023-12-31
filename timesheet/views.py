from django.contrib.auth import get_user_model
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.db.models.functions import TruncMonth, Extract
from django.db.models import F, Sum, Q, FloatField, ExpressionWrapper, DurationField, DecimalField
from timesheet.models import TimeSheet, EmployeeSchedule, TimeSheetChoices
from timesheet.serializers import CheckInSerializer, CheckOutSerializer, TimeSheetModelSerializer, \
    TimeSheetListSerializer, TimeSheetUpdateSerializer, ChangeTimeSheetSerializer, TakeTimeOffSerializer, \
    VacationTimeSheetSerializer, CreateFutureTimeSheetSerializer, MonthHoursSerializer, MonthHoursValidationSerializer, \
    UpdateTimeSheetSerializer
from timesheet.services import create_check_in_timesheet, get_last_timesheet_action, create_check_out_timesheet, \
    update_timesheet, change_timesheet, set_took_off, create_vacation, get_timesheet_by_month, create_future_time_sheet
from timesheet.utils import EmployeeTooFarFromDepartment, FillUserStatistic, CheckInAlreadyExistsException
from utils.manual_parameters import QUERY_YEAR, QUERY_MONTH, QUERY_ROLE, QUERY_MONTHS
from utils.permissions import TimeSheetPermissions, ChangeTimeSheetPermissions, CheckPermission
from utils.tools import log_exception
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TimeSheetViewSet(ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = TimeSheetModelSerializer
    permission_classes = (TimeSheetPermissions,)
    queryset = TimeSheet.objects.all().select_related('role', 'role__department')
    pagination_class = None

    @swagger_auto_schema(manual_parameters=[QUERY_ROLE, QUERY_MONTH, QUERY_YEAR])
    def list(self, request, *args, **kwargs):
        """
        Получить расписание за определенный месяц на роль
        """
        serializer = TimeSheetListSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = get_timesheet_by_month(**serializer.validated_data)
        return Response(data=data)

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
    permission_classes = (CheckPermission,)

    @swagger_auto_schema(request_body=CheckInSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = CheckInSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            create_check_in_timesheet(request.user.role, serializer.validated_data)
            return Response({'message': 'created'})
        except EmployeeTooFarFromDepartment as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except CheckInAlreadyExistsException as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except EmployeeSchedule.DoesNotExist:
            return Response({'message': _("Сегодня нерабочий день")}, status.HTTP_423_LOCKED)
        except IntegrityError as e:
            log_exception(e, 'Error in CheckInViewSet.create() IntegrityError')
            return Response({'message': _("Вы уже осуществили check in сегодня")}, status.HTTP_423_LOCKED)
        except Exception as e:
            log_exception(e, 'Error in CheckInViewSet.create() Exception')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TakeTimeOffView(CreateModelMixin, GenericViewSet):
    permission_classes = (CheckPermission,)

    @swagger_auto_schema(request_body=TakeTimeOffSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = TakeTimeOffSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            message, status_code = set_took_off(self.request.user.role, serializer.validated_data)
            return Response(message, status_code)
        except ValueError as e:
            return Response({'message': str(e)}, status=status.HTTP_423_LOCKED)

        except Exception as e:
            log_exception(e, 'Error in TookOffViewSet.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckOutViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (CheckPermission,)

    @swagger_auto_schema(request_body=CheckOutSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = CheckOutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            result = create_check_out_timesheet(request.user.role, serializer.validated_data)
            if result is False:
                return Response({'message': _('Нужно сделать check in заново'), 'code': 're-check-in'}, status=status.HTTP_423_LOCKED)
            return Response({'message': 'created'})
        except FillUserStatistic as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except Exception as e:
            log_exception(e, 'Error in CheckOutViewSet.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangeTimeSheetViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = (ChangeTimeSheetPermissions,)
    serializer_class = ChangeTimeSheetSerializer
    queryset = TimeSheet.objects.all()

    @swagger_auto_schema(requet_body=ChangeTimeSheetSerializer)
    def update(self, request, *args, **kwargs):
        """
        изменить существующую или заполнить юзер статистику за него. STATUSES:
            ON_TIME = 1
            LATE = 2
            ABSENT = 3
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            change_timesheet(instance, serializer.validated_data)
            return Response({'message': 'updated'})
        except Exception as e:
            log_exception(e, 'Error in ChangeTimeSheetViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class VacationTimeSheetViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (ChangeTimeSheetPermissions,)
    serializer_class = VacationTimeSheetSerializer
    queryset = TimeSheet.objects.all()

    @swagger_auto_schema(requet_body=VacationTimeSheetSerializer)
    def create(self, request, *args, **kwargs):
        """
        Создать отпуск для работника
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            response, status_code = create_vacation(serializer.validated_data)
            return Response(response, status=status_code)
        except IntegrityError:
            return Response({'message': _("В указанный промежуток уже есть check_in")}, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_exception(e, 'Error in ChangeTimeSheetViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateFutureTimeSheetAPI(APIView):
    permission_classes = (IsAuthenticated,)
    # permission_classes = (ChangeTimeSheetPermissions,)

    @swagger_auto_schema(request_body=CreateFutureTimeSheetSerializer)
    def post(self, request):
        serializer = CreateFutureTimeSheetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response, status_code = create_future_time_sheet(**serializer.validated_data)
        return Response(response, status=status_code)


class UpdateTimeSheetAPI(UpdateModelMixin, GenericViewSet):
    permission_classes = (ChangeTimeSheetPermissions,)
    serializer_class = UpdateTimeSheetSerializer
    queryset = TimeSheet.objects.order_by()


class MonthHoursViewSet(ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('role',)
    serializer_class = MonthHoursSerializer
    filter_serializer = None

    def get_queryset(self):

        return TimeSheet.objects.filter(
            check_in_new__isnull=False,
            check_out_new__isnull=False,
            status__in=[TimeSheetChoices.ON_TIME, TimeSheetChoices.LATE]
        ).annotate(
            month=TruncMonth('check_in_new')
        ).values(
            'month'
        ).annotate(
            total_duration=Sum(
                (Extract('check_out_new', 'epoch') - Extract('check_in_new', 'epoch')) / 3600.0,
                output_field=FloatField()
            )
        ).exclude(
            Q(total_duration=None) | Q(total_duration=0)
        ).order_by(
            'month'
        )

    def filter_queryset(self, queryset):
        data = self.filter_serializer.validated_data

        if 'year' in data:
            if 'months' in data:
                return queryset.filter(created_at__year=data['year'], role_id=data['role'],
                                       created_at__month__in=data['months']).distinct().order_by('month')
            return queryset.filter(created_at__year=data['year'], role_id=data['role']).distinct().order_by('month')
        else:
            return queryset.filter(role_id=data['role']).distinct().order_by('month')

    @swagger_auto_schema(manual_parameters=[QUERY_YEAR, QUERY_MONTHS])
    def list(self, request, *args, **kwargs):
        """
        Получить кол-во баллов за каждый выбранный месяц в году по роли, или за весь период
        """
        self.filter_serializer = MonthHoursValidationSerializer(data=request.query_params)
        self.filter_serializer.is_valid(raise_exception=True)
        return super().list(request, *args, **kwargs)
