from rest_framework.viewsets import ModelViewSet

from bepro_statistics.models import UserStatistic
from bepro_statistics.serializers import StatisticSerializer, UserStatisticSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.transaction import atomic
from bepro_statistics.services import get_statistics_queryset, create_statistic, get_user_statistic
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from utils.manual_parameters import QUERY_USER, QUERY_STATISTIC_TYPE
from django.contrib.auth import get_user_model
User = get_user_model()


class StatisticViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = StatisticSerializer

    def get_queryset(self):
        return get_statistics_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with atomic():
            create_statistic(serializer)
        return Response({'message': 'created'}, status=status.HTTP_201_CREATED)


class UserStatisticViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserStatisticSerializer
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
