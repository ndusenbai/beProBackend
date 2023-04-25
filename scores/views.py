from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from scores.serializers import ReasonSerializer, ScoreModelSerializer, MonthScoresValidationSerializer, ScoreSerializer, \
    MonthScoresSerializer, ScoreFeedSerializer
from scores.models import Reason, Score
from scores.services import create_score, get_score_feed
from utils.manual_parameters import QUERY_YEAR, QUERY_MONTHS, QUERY_END_DATE, QUERY_START_DATE, QUERY_REASONS, \
    QUERY_FULL_NAME
from utils.permissions import ReasonPermissions, MonthScorePermissions, ScorePermission


class ReasonViewSet(ModelViewSet):
    permission_classes = (ReasonPermissions,)
    serializer_class = ReasonSerializer
    queryset = Reason.objects.order_by('name')
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('company',)
    http_method_names = ['get', 'post', 'put', 'delete']


class ScoreViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = (ScorePermission,)
    queryset = Score.objects.order_by('-created_at')
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('reason__name', 'created_by__first_name', 'created_by__last_name')
    filterset_fields = ('role',)
    filter_serializer = None

    def get_serializer_class(self):
        if self.action == 'list':
            return ScoreModelSerializer
        return ScoreSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if self.filter_serializer:
            data = self.filter_serializer.validated_data

            if 'year' in data and 'months' in data:
                return queryset.filter(created_at__year=data['year'], created_at__month__in=data['months'])

        return queryset

    @swagger_auto_schema(manual_parameters=[QUERY_YEAR, QUERY_MONTHS])
    def list(self, request, *args, **kwargs):
        self.filter_serializer = MonthScoresValidationSerializer(data=request.query_params)
        self.filter_serializer.is_valid(raise_exception=True)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_score(request.user, serializer.validated_data)
        return Response({'message': 'created'})


class MonthScoresViewSet(ListModelMixin, GenericViewSet):
    permission_classes = (MonthScorePermissions,)
    serializer_class = MonthScoresSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('role',)
    filter_serializer = None

    def get_queryset(self):
        return Score.objects\
            .annotate(month=TruncMonth('created_at')).values('month')\
            .annotate(score=100+Sum('points')).values('month', 'score')

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
        self.filter_serializer = MonthScoresValidationSerializer(data=request.query_params)
        self.filter_serializer.is_valid(raise_exception=True)
        return super().list(request, *args, **kwargs)


class ScoreFeedListView(ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ScoreFeedSerializer

    @swagger_auto_schema(manual_parameters=[QUERY_START_DATE, QUERY_END_DATE, QUERY_REASONS, QUERY_FULL_NAME])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        extra_kwargs = {}
        if self.request.GET.get('start_date') and self.request.GET.get('end_date'):
            start_date = self.request.GET.get('start_date')
            end_date = self.request.GET.get('end_date')
            extra_kwargs['created_at__date__range'] = [start_date, end_date]

        if self.request.GET.get('reasons'):
            reasons_list = []
            reasons = self.request.GET.get('reasons').split(',')
            for reason in reasons:
                reasons_list.append(reason)
            extra_kwargs['name__in'] = reasons_list

        full_name = self.request.GET.get('full_name')
        if full_name:
            query = Q(role__user__first_name__icontains=full_name) | Q(role__user__last_name__icontains=full_name)
            if " " in full_name:
                first_name, last_name = full_name.split(" ")
                query |= Q(role__user__first_name__icontains=first_name, role__user__last_name__icontains=last_name) | Q(
                    role__user__first_name__icontains=last_name, role__user__last_name__icontains=first_name)

            return queryset.filter(query, **extra_kwargs)

        return queryset.filter(**extra_kwargs)

    def get_queryset(self):
        return get_score_feed(self.request.user)
