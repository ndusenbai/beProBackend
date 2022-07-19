from typing import OrderedDict

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpRequest
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.apps import apps

from auth_user.models import AssistantTypes
from auth_user.serializers import ObserverCreateSerializer, UserModelSerializer
from django.db.models import Q

from companies.models import Role, RoleChoices, Company
from utils.tools import log_exception

User = get_user_model()
password_reset_token = PasswordResetTokenGenerator()


def send_email(subject: str, to_list: list, template_name: str, context: dict):
    from_mail = settings.EMAIL_HOST_USER
    email_tmp = render_to_string(
        template_name,
        context
    )
    msg = EmailMultiAlternatives(subject, email_tmp, from_mail, to_list)
    msg.attach_alternative(email_tmp, "text/html")
    msg.send()


def change_password(user: User, validated_data: dict) -> None:
    if user.check_password(validated_data.get('old_password')):
        user.set_password(validated_data.get('new_password'))
        user.save()
    else:
        raise serializers.ValidationError('Old password incorrect', code='incorrect_old')


def forgot_password(request: HttpRequest, validated_data: dict):
    user = get_object_or_404(User, **validated_data)
    domain = get_domain(request)
    context = {
        'domain': domain,
        'token': password_reset_token.make_token(user),
        'uid': urlsafe_base64_encode(force_bytes(user.pk))
    }
    send_email(subject='Смена пароля', to_list=[user.email], template_name='reset_password.html', context=context)


def change_password_after_forgot(uid, token, validated_data: dict):
    pk = force_str(urlsafe_base64_decode(uid))
    try:
        user = User.objects.get(pk=pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and password_reset_token.check_token(user, token):
        user.set_password(validated_data.get('password'))
        user.save()
    else:
        raise serializers.ValidationError('Token expired', code='expired_token')


def check_link_after_forgot(uid, token) -> bool:
    pk = force_str(urlsafe_base64_decode(uid))
    try:
        user = User.objects.get(pk=pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    return bool(user is not None and password_reset_token.check_token(user, token))


def send_created_account_notification(request: HttpRequest, user: User, password: str) -> None:
    subject = 'Добро пожаловать!'
    from_mail = settings.EMAIL_HOST_USER
    to_list = [user.email, ]
    domain = get_domain(request)
    email_tmp = render_to_string(
        'company_registered_notification.html',
        {'domain': domain, 'login': user.email, 'password': password}
    )
    msg = EmailMultiAlternatives(subject, email_tmp, from_mail, to_list)
    msg.attach_alternative(email_tmp, "text/html")
    msg.send()


def get_domain(request: HttpRequest) -> str:
    current_site = get_current_site(request)
    domain_name = current_site.domain
    if 'media.' in domain_name:
        domain_name = domain_name.replace('media.', '')

    protocol = 'https://' if request.is_secure() else 'http://'
    return protocol + domain_name


def create_observer_and_role(serializer: ObserverCreateSerializer, user):
    first_name = serializer.validated_data['first_name']
    last_name = serializer.validated_data['last_name']
    middle_name = serializer.validated_data['middle_name']
    email = serializer.validated_data['email']
    observer = User.objects.filter(email=email)
    if not observer.exists():
        observer = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            email=email,
        )
    else:
        observer = observer.first()
    apps.get_model(
        app_label='companies',
        model_name='Role'
    ).objects.create(
        company=user.selected_company,
        department=None,
        role=RoleChoices.OBSERVER,
        user=observer
    )
    return observer


def get_user_list(company):
    return apps.get_model(
        app_label='companies',
        model_name='Role'
    ).objects.filter(company=company)


def create_assistant(serializer):
    first_name = serializer.validated_data['first_name']
    last_name = serializer.validated_data['last_name']
    middle_name = serializer.validated_data['middle_name']
    email = serializer.validated_data['email']
    phone_number = serializer.validated_data['phone_number']
    assistant_type = serializer.validated_data['assistant_type']
    assistant = User.objects.filter(email=email)

    if not assistant.exists():

        assistant = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                email=email,
                phone_number=phone_number,
                is_staff=True,
                assistant_type=assistant_type
            )
    else:
        assistant = assistant.first()
        assistant.first_name = first_name
        assistant.last_name = last_name
        assistant.middle_name = middle_name
        assistant.phone_number = phone_number
        assistant.save()

    return assistant


def assistants_queryset():
    return User.objects.filter(~Q(assistant_type=AssistantTypes.NON_ASSISTANT), is_staff=True)


def get_user_role(user: User) -> str:
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
            owner_companies = Company.objects.filter(owner=user)

            if owner_companies.exists():
                role = 'owner'
            elif role_type == RoleChoices.HR:
                role = 'hr'
            elif role_type == RoleChoices.OBSERVER:
                role = 'observer'
            elif role_type == RoleChoices.EMPLOYEE:
                role = 'employee'
            elif role_type == RoleChoices.HEAD_OF_DEPARTMENT:
                role = 'head_of_department'

        return role
    except Exception as e:
        log_exception(e, 'Error in get_user_role')
        return 'no_role'


def get_additional_user_info(email: str) -> dict:
    user = User.objects.get(email=email)
    user_data = UserModelSerializer(user).data
    user_data['role'] = get_user_role(user)
    try:
        user_data['role_id'] = user.role.id
    except:
        user_data['role_id'] = None
    return user_data


def change_selected_company(request_user: User, data: OrderedDict):
    new_selected_company = data['new_selected_company']
    if new_selected_company.owner.id == request_user.id:
        request_user.selected_company = new_selected_company
        request_user.save()
        return True
    return False


def activate_owner_companies(owner_id):
    Company.objects.filter(owner_id=owner_id).update(is_active=True)


def deactivate_owner_companies(owner_id):
    Company.objects.filter(owner_id=owner_id).update(is_active=False)


def get_user_profile(user, serializer_class):
    data = dict()
    name_tuple = (user.first_name, user.middle_name, user.last_name)
    data['id'] = user.id
    data['full_name'] = " ".join([name.strip() for name in name_tuple if name])
    data['department_name'] = user.role.department.name
    data['email'] = user.email
    data['phone_number'] = user.phone_number
    serializer = serializer_class(data=data, many=False)
    serializer.is_valid()

    return serializer.data, 200


def update_user_profile(user, serializer):
    data = serializer.validated_data
    full_name = [name.strip() for name in data.pop('full_name').split(" ")]

    for index, key in enumerate(("middle_name", "first_name", "last_name")):
        data[key] = full_name[index] if index < len(full_name) else ""

    serializer = UserModelSerializer(user, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return serializer.data, 200
