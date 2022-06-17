from rest_framework.viewsets import ModelViewSet
from bepro_statistics.serializers import StatisticSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.transaction import atomic
from bepro_statistics.services import get_statistics_queryset, create_statistic
from rest_framework.response import Response
from rest_framework import status


class StatisticViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = StatisticSerializer

    def get_queryset(self):
        return get_statistics_queryset(self.request.user.selected_company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with atomic():
            statistic = create_statistic(serializer, request.user)
            print(statistic)
        return Response({'message': 'created'}, status=status.HTTP_201_CREATED)
