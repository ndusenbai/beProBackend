from django.db.transaction import atomic
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from auth_user.serializers import ChangePasswordSerializer, EmailSerializer, ForgotPasswordResetSerializer, \
    ObserverListSerializer, ObserverCreateSerializer, EmployeeListSerializer, AssistantSerializer, \
    ChangeSelectedCompanySerializer, OwnerSerializer, UserProfileSerializer, ForgotPasswordWithPinResetSerializer
from auth_user.services import change_password, forgot_password, change_password_after_forgot, \
    check_link_after_forgot, create_observer_and_role, get_user_list, create_assistant, assistants_queryset, \
    get_additional_user_info, change_selected_company, activate_owner_companies, deactivate_owner_companies, \
    get_user_profile, update_user_profile, forgot_password_with_pin, check_code_after_forgot, \
    change_password_with_code_after_forgot
from utils.manual_parameters import QUERY_CODE

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
        resp.data['user'] = get_additional_user_info(request.data['email'])
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


class OwnerViewSet(ListModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = OwnerSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('last_name', 'first_name', 'middle_name', 'phone_number', 'company_name')

    def get_queryset(self):
        from django.db.models import Count, F
        return User.objects.annotate(
                employees_count=Count('selected_company__roles', distinct=True),
                company_name=F('selected_company__name'),
                is_company_active=F('selected_company__is_active'),)\
            .alias(owned_companies_count=Count('owned_companies', distinct=True))\
            .filter(owned_companies_count__gt=0)\
            .only('id', 'last_name', 'first_name', 'middle_name', 'phone_number')\
            .order_by('id')


class ActivateOwnerCompaniesViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        activate_owner_companies(kwargs['pk'])
        return Response({'message': 'Success'})


class DeactivateOwnerCompaniesViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        deactivate_owner_companies(kwargs['pk'])
        return Response({'message': 'Success'})


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        response, status_code = get_user_profile(self.request.user, self.serializer_class)
        return Response(response, status=status_code)


class UpdateUserProfileView(UpdateModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        response, status_code = update_user_profile(instance, serializer,)

        return Response(response, status=status_code)
