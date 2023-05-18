import datetime
from typing import OrderedDict

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpRequest
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.timezone import now
from django.db.models import Q, Count, F
from django.db import IntegrityError
from django.db.transaction import atomic
from rest_framework import serializers

from auth_user.models import AssistantTypes, AcceptCode
from auth_user.serializers import UserModelSerializer
from auth_user.tasks import send_email
from companies.models import RoleChoices, Company
from utils.tools import log_exception

User = get_user_model()
password_reset_token = PasswordResetTokenGenerator()


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
    send_email.delay(subject='Смена пароля', to_list=[user.email], template_name='reset_password.html', context=context)


def get_accept_code(user):
    try:
        accept_code = AcceptCode.objects.create(user=user)
        return accept_code.code
    except IntegrityError:
        get_accept_code(user)


def forgot_password_with_pin(request: HttpRequest, validated_data: dict):
    domain = get_domain(request)
    user = get_object_or_404(User, **validated_data)
    accept_code = get_accept_code(user)
    context = {
        'accept_code': accept_code,
        'domain': domain,
    }
    send_email.delay(subject='Смена пароля', to_list=[user.email], template_name='reset_password_with_pin.html', context=context)


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


def change_password_with_code_after_forgot(validated_data: dict):
    code = validated_data.pop('code')
    validation_dict = check_code_after_forgot(code)

    if not validation_dict['status']:
        raise serializers.ValidationError(validation_dict['message'], code='code_validation_error')

    accept_code = AcceptCode.objects.select_related('user').get(code=code, is_expired=False, is_accepted=False)
    accept_code.user.set_password(validated_data.get('password'))
    accept_code.user.save()

    accept_code.is_accepted = True
    accept_code.save()


def check_link_after_forgot(uid, token) -> bool:
    pk = force_str(urlsafe_base64_decode(uid))
    try:
        user = User.objects.get(pk=pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    return bool(user is not None and password_reset_token.check_token(user, token))


def check_code_after_forgot(code) -> dict:
    if not code:
        return {'status': False, 'message': 'Input code'}

    accept_code = AcceptCode.objects.filter(code=code, is_accepted=False, is_expired=False)

    if not accept_code.exists():
        return {'status': False, 'message': 'Wrong code'}

    accept_code = accept_code.first()

    if accept_code.expiration < now():
        accept_code.is_expired = True
        accept_code.save()
        return {'status': False, 'message': 'Code is expired'}

    return {'status': True, 'message': 'Is active'}


def get_domain(request: HttpRequest) -> str:
    current_site = get_current_site(request)
    domain_name = current_site.domain
    if 'media.' in domain_name:
        domain_name = domain_name.replace('media.', '')

    protocol = 'https://' if request.is_secure() else 'http://'
    return protocol + domain_name


@atomic
def create_assistant(serializer):
    first_name = serializer.validated_data['first_name']
    last_name = serializer.validated_data['last_name']
    middle_name = serializer.validated_data['middle_name']
    email = serializer.validated_data['email']
    phone_number = serializer.validated_data['phone_number']
    assistant_type = serializer.validated_data['assistant_type']
    assistant = User.objects.filter(email=email)

    if not assistant.exists():

        assistant = User.objects.create_user(
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
            if Company.objects.filter(owner=user).exists():
                role = 'owner'
                return role

            role_type = user.role.role
            if role_type == RoleChoices.HR:
                role = 'hr'
            elif role_type == RoleChoices.OBSERVER:
                role = 'observer'
            elif role_type == RoleChoices.EMPLOYEE:
                role = 'employee'
            elif role_type == RoleChoices.HEAD_OF_DEPARTMENT and user.role.department.is_hr:
                role = 'head_of_hr_department'
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

    try:
        user_data['departament'] = user.role.department.id
    except:
        user_data['departament'] = None

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


def update_user_profile(user, serializer):
    data = serializer.validated_data
    full_name = [name.strip() for name in data.pop('full_name').split(" ")]

    for index, key in enumerate(("last_name", "first_name", "middle_name")):
        data[key] = full_name[index] if index < len(full_name) else ""

    serializer = UserModelSerializer(user, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return serializer.data, 200


def update_user(instance: User, data) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def get_owners_qs():
    return User.objects.annotate(
            employees_count=Count('selected_company__roles', distinct=True),
            company_name=F('selected_company__name'),
            is_company_active=F('selected_company__is_active'),) \
        .alias(owned_companies_count=Count('owned_companies', distinct=True)) \
        .filter(owned_companies_count__gt=0) \
        .order_by('id')


def update_email(request, user, email_new):
    existing_email = User.objects.filter(email=email_new)
    if existing_email.exists():
        return False
    user.email_new = email_new
    user.save()
    domain = get_domain(request)
    context = {
        'domain': domain,
        'token': password_reset_token.make_token(user),
        'uid': urlsafe_base64_encode(force_bytes(user.pk))
    }
    # need to return send_email.delay in future
    send_email(subject='Смена почты', to_list=[email_new], template_name='reset_email.html', context=context)
    return True


def set_new_email(uid, token):
    pk = force_str(urlsafe_base64_decode(uid))
    try:
        user = User.objects.get(pk=pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and password_reset_token.check_token(user, token):
        user.email = user.email_new
        user.email_new = None
        user.save()
    else:
        raise serializers.ValidationError('Token expired', code='expired_token')


