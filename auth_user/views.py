from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth_user.serializers import ChangePasswordSerializer, EmailSerializer, ForgotPasswordResetSerializer, \
    UserModelSerializer
from auth_user.services import change_password, forgot_password, change_password_after_forgot, check_link_after_forgot

User = get_user_model()


class UserView(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.order_by()
    serializer_class = UserModelSerializer


class ChangePasswordView(GenericViewSet):
    queryset = User.objects.order_by()
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated, )

    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password(request.user, serializer.validated_data)
        return Response({'message': 'updated'}, status=status.HTTP_200_OK)


class ForgotPasswordView(GenericViewSet):
    queryset = User.objects.order_by()

    def get_serializer_class(self):
        if self.action == 'reset_password':
            return EmailSerializer
        return ForgotPasswordResetSerializer

    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        forgot_password(request, serializer.validated_data)
        return Response({'message': 'email_sent'})

    def new_password(self, request, uid, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password_after_forgot(uid, token, serializer.validated_data)
        return Response({'message': 'changed'})

    def check_link(self, request, uid, token):
        return Response({
            'active': check_link_after_forgot(uid, token)
        })
