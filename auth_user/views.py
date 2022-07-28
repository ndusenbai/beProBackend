from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from auth_user.serializers import ChangePasswordSerializer, EmailSerializer, ForgotPasswordResetSerializer, \
    AssistantSerializer, \
    ChangeSelectedCompanySerializer, OwnerSerializer, UserProfileSerializer, ForgotPasswordWithPinResetSerializer, \
    AssistantUpdateSerializer, OwnerRetrieveSerializer
from auth_user.services import change_password, forgot_password, change_password_after_forgot, \
    check_link_after_forgot, create_assistant, assistants_queryset, get_additional_user_info, change_selected_company, \
    activate_owner_companies, deactivate_owner_companies, update_user_profile, forgot_password_with_pin, \
    check_code_after_forgot, change_password_with_code_after_forgot, update_user, get_owners_qs

from utils.manual_parameters import QUERY_CODE
from utils.permissions import IsAssistantProductOrSuperuser, IsSuperuser

User = get_user_model()


class ChangePasswordView(GenericViewSet):
    queryset = User.objects.order_by()
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated, )

    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.pop('user', request.user)
        change_password(user, serializer.validated_data)
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


class ForgotPasswordWithPinView(GenericViewSet):
    queryset = User.objects.order_by()

    def get_serializer_class(self):
        if self.action == 'reset_password':
            return EmailSerializer
        return ForgotPasswordWithPinResetSerializer

    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        forgot_password_with_pin(serializer.validated_data)
        return Response({'message': 'email_sent'})

    def new_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password_with_code_after_forgot(serializer.validated_data)
        return Response({'message': 'changed'})

    @swagger_auto_schema(manual_parameters=[QUERY_CODE])
    def check_code(self, request):
        return Response(check_code_after_forgot(request.GET.get('code')))


class AssistantViewSet(ModelViewSet):
    permission_classes = (IsSuperuser,)
    filter_backends = (SearchFilter,)
    search_fields = ('last_name', 'first_name', 'middle_name', 'phone_number',)
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        return assistants_queryset()

    def get_serializer_class(self):
        if self.action == 'update':
            return AssistantUpdateSerializer
        return AssistantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assistant = create_assistant(serializer)
        return Response(self.get_serializer(assistant).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=AssistantUpdateSerializer)
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_user(self.get_object(), serializer.validated_data)
        return Response({'message': 'updated'}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        user_data = get_additional_user_info(request.data['email'])
        resp = super().post(request, *args, **kwargs)
        resp.data['user'] = user_data

        if user_data['role'] == 'no_role':
            return Response({'message': 'Данный пользователь не существует'}, status=status.HTTP_400_BAD_REQUEST)

        return resp


class ChangeSelectedCompanyViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = ChangeSelectedCompanySerializer
    http_method_names = ['put']

    def update(self, request, *args, **kwargs):
        """
        id = юзер айди владельца
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = change_selected_company(self.get_object(), serializer.validated_data)
        if not result:
            return Response({'message': 'you are not the owner of company'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'message': 'updated'})


class OwnerViewSet(ListModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAssistantProductOrSuperuser, )
    filter_backends = (SearchFilter,)
    search_fields = ('last_name', 'first_name', 'middle_name', 'phone_number', 'company_name')

    def get_queryset(self):
        return get_owners_qs()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OwnerRetrieveSerializer
        return OwnerSerializer


class ActivateOwnerCompaniesViewSet(APIView):
    permission_classes = (IsAssistantProductOrSuperuser,)

    def post(self, request, **kwargs):
        activate_owner_companies(kwargs['pk'])
        return Response({'message': 'Success'})


class DeactivateOwnerCompaniesViewSet(APIView):
    permission_classes = (IsAssistantProductOrSuperuser,)

    def post(self, request, **kwargs):
        deactivate_owner_companies(kwargs['pk'])
        return Response({'message': 'Success'})


class UserProfileView(UpdateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        response, status_code = update_user_profile(request.user, serializer,)

        return Response(response, status=status_code)
