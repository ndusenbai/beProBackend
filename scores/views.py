from django.db.models import Sum
from django.db.models.functions import TruncMonth
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from scores.serializers import ReasonSerializer, ScoreModelSerializer, MonthScoresValidationSerializer, ScoreSerializer, \
    MonthScoresSerializer
from scores.models import Reason, Score
from scores.services import create_score
from utils.manual_parameters import QUERY_YEAR, QUERY_MONTHS


class ReasonViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReasonSerializer
    queryset = Reason.objects.order_by('name')
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('company',)
    http_method_names = ['get', 'post', 'put', 'delete']


class ScoreViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Score.objects.order_by('-created_at')
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('reason__name', 'created_by__first_name', 'created_by__last_name')
    filterset_fields = ('role',)

    def get_serializer_class(self):
        if self.action == 'list':
            return ScoreModelSerializer
        return ScoreSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_score(request.user, serializer.validated_data)
        return Response({'message': 'created'})


class MonthScoresViewSet(ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
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
        return queryset.filter(created_at__year=data['year'], role_id=data['role'], created_at__month__in=data['months'])

    @swagger_auto_schema(manual_parameters=[QUERY_YEAR, QUERY_MONTHS])
    def list(self, request, *args, **kwargs):
        """
        Получить кол-во баллов за каждый выбранный месяц в году по роли
        """
        self.filter_serializer = MonthScoresValidationSerializer(data=request.query_params)
        self.filter_serializer.is_valid(raise_exception=True)
        return super().list(request, *args, **kwargs)
