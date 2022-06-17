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
