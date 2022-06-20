from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from auth_user.serializers import ChangePasswordSerializer, EmailSerializer, ForgotPasswordResetSerializer, \
    ObserverListSerializer, ObserverCreateSerializer, EmployeeListSerializer, AssistantSerializer
from auth_user.services import change_password, forgot_password, change_password_after_forgot, check_link_after_forgot, \
    create_observer_and_role, get_user_list, create_assistant, assistants_queryset
from django.db.transaction import atomic
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


class ObserverViewSet(ListModelMixin,
                      CreateModelMixin,
                      DestroyModelMixin,
                      GenericViewSet):
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == 'list':
            return ObserverListSerializer
        elif self.action == 'create':
            return ObserverCreateSerializer

    def get_queryset(self):
        return get_user_list(self.request.user.selected_company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with atomic():
            create_observer_and_role(serializer, request.user)
        return Response({'message': 'created'}, status=status.HTTP_201_CREATED)


class EmployeeListView(ListModelMixin, GenericViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeeListSerializer

    def get_queryset(self):
        return get_user_list(self.request.user.selected_company)


class AssistantViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AssistantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with atomic():
            assistant = create_assistant(serializer)
        return Response(self.get_serializer(assistant).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return assistants_queryset()
