from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from auth_user.models import AssistantTypes
from auth_user.serializers import ChangePasswordSerializer, EmailSerializer, ForgotPasswordResetSerializer, \
    UserSerializer, ObserverListSerializer, ObserverCreateSerializer, EmployeeListSerializer, AssistantSerializer, \
    CreateEmployeeSerializer
from auth_user.services import change_password, forgot_password, change_password_after_forgot, check_link_after_forgot, \
    create_observer_and_role, get_user_list, create_assistant, assistants_queryset, create_employee, update_user
from companies.models import Role, RoleChoices
from companies.serializers import RoleSerializer
from utils.tools import log_exception

from django.db.transaction import atomic

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return User.objects.prefetch_related(Prefetch('employee_schedules', to_attr='schedules'))

    @swagger_auto_schema(request_body=CreateEmployeeSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateEmployeeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            create_employee(serializer.validated_data)
            return Response({'message': 'created'})
        except Exception as e:
            log_exception(e, 'Error in UserViewSet.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            data = self.get_serializer(instance).data
            role = Role.objects.get(company=request.user.selected_company, user_id=kwargs['pk'])
            data['role'] = RoleSerializer(role).data
            return Response(data)
        except Exception as e:
            log_exception(e, 'Error in UserViewSet.retrieve()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            serializer = CreateEmployeeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            update_user(self.get_object(), serializer.validated_data, request.user)
            return Response({'message': 'updated'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, 'Error in DepartmentViewSet.update()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        user = User.objects.get(email=request.data['email'])
        resp.data['selected_company_id'] = user.selected_company_id
        try:
            role = ''

            if user.is_superuser:
                role = 'superuser'
            elif user.assistant_type == AssistantTypes.MARKETING:
                role = 'admin_marketing'
            elif user.assistant_type == AssistantTypes.PRODUCTION_WORKERS:
                role = 'admin_production_worker'
            else:
                role_type = Role.objects.get(user=user, company=user.selected_company).role

                if role_type == RoleChoices.OWNER:
                    role = 'owner'
                elif role_type == RoleChoices.HR:
                    role = 'hr'
                elif role_type == RoleChoices.OBSERVER:
                    role = 'observer'
                elif role_type == RoleChoices.EMPLOYEE:
                    role = 'employee'
                elif role_type == RoleChoices.HEAD_OF_DEPARTMENT:
                    role = 'head_of_department'

            resp.data['role'] = role
        except Exception as e:
            resp.data['error_message'] = str(e)
            log_exception(e, 'Error in CustomTokenObtainPairView.post()')
        return resp
