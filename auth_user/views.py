from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth_user.serializers import ChangePasswordSerializer
from auth_user.services import change_password

User = get_user_model()


class ChangePasswordView(GenericViewSet):
    queryset = User.objects.order_by()
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated, )

    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password(request.user, serializer.validated_data)
        return Response({'message': 'updated'}, status=status.HTTP_200_OK)
