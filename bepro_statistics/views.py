from django.db import IntegrityError
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from bepro_statistics.models import UserStatistic, Statistic
from bepro_statistics.serializers import StatisticSerializer, UserStatisticModelSerializer, \
    CreateUserStatSerializer, StatsForUserSerializer, HistoryStatsForUserSerializer
from bepro_statistics.services import get_statistics_queryset, create_statistic, get_user_statistic, \
    create_user_statistic, get_stats_for_user, get_history_stats_for_user
from utils.manual_parameters import QUERY_USER, QUERY_ROLE, QUERY_SUNDAY, QUERY_MONDAY, QUERY_STATISTIC_TYPE_LIST
from utils.tools import log_exception

User = get_user_model()


class StatisticViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = StatisticSerializer

    def get_queryset(self):
        return get_statistics_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_statistic(serializer)
        return Response({'message': 'created'}, status=status.HTTP_201_CREATED)


class UserStatisticViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserStatisticModelSerializer
    queryset = UserStatistic.objects.all()


class UserStatisticAPI(APIView):

    @swagger_auto_schema(manual_parameters=[QUERY_USER])
    def get(self, request):
        if self.request.GET.get('user_id'):

            try:
                user = User.objects.get(id=self.request.GET.get('user_id'))
                user_statistics = get_user_statistic(user)
                return Response(user_statistics)
            except User.DoesNotExist:
                return Response({'message': 'No such user'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Enter user id'}, status=status.HTTP_400_BAD_REQUEST)


class StatsForUser(ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Statistic.objects.all()
    serializer_class = StatsForUserSerializer

    @swagger_auto_schema(manual_parameters=[QUERY_ROLE])
    def list(self, request, *args, **kwargs):
        """
        Получить все статистики по роли на текущую неделю
        """
        data = get_stats_for_user(request)
        return Response(data=data)


class HistoryStats(ListModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Statistic.objects.all()
    serializer_class = HistoryStatsForUserSerializer

    @swagger_auto_schema(manual_parameters=[QUERY_ROLE, QUERY_MONDAY, QUERY_SUNDAY, QUERY_STATISTIC_TYPE_LIST])
    def list(self, request, *args, **kwargs):
        """
        Получить все статистики по роли на заданную неделю
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = get_history_stats_for_user(request.user, serializer.validated_data)
        return Response(data=data)


class CreateUserStat(CreateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateUserStatSerializer

    @swagger_auto_schema(requet_body=CreateUserStatSerializer)
    def create(self, request, *args, **kwargs):
        """
        заполнить юзер статистику на последний день когда работник чекинился
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            create_user_statistic(request.user.role, serializer.validated_data)
            return Response({'message': 'created'})
        except IntegrityError:
            return Response({'message': 'Статистика уже заполнена'}, status.HTTP_423_LOCKED)
        except Exception as e:
            log_exception(e, 'Error in CreateUserStat.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
