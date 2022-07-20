from auth_user.celery import app
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpRequest
from django.contrib.sites.shortcuts import get_current_site


def get_domain(request: HttpRequest) -> str:
    current_site = get_current_site(request)
    domain_name = current_site.domain
    if 'media.' in domain_name:
        domain_name = domain_name.replace('media.', '')

    protocol = 'https://' if request.is_secure() else 'http://'
    return protocol + domain_name


@app.task
def send_email(subject: str, to_list: list, template_name: str, context: dict):
    from_mail = settings.EMAIL_HOST_USER
    email_tmp = render_to_string(
        template_name,
        context
    )
    msg = EmailMultiAlternatives(subject, email_tmp, from_mail, to_list)
    msg.attach_alternative(email_tmp, "text/html")
    msg.send()


@app.task
def send_created_account_notification(domain, email, password: str) -> None:
    subject = 'Добро пожаловать!'
    from_mail = settings.EMAIL_HOST_USER
    to_list = [email, ]
    email_tmp = render_to_string(
        'company_registered_notification.html',
        {'domain': domain, 'login': email, 'password': password}
    )
    msg = EmailMultiAlternatives(subject, email_tmp, from_mail, to_list)
    msg.attach_alternative(email_tmp, "text/html")
    msg.send()


@app.task
def send_invitation(email, password):
    subject = 'Добро пожаловать!'
    from_mail = settings.EMAIL_HOST_USER
    to_list = [email, ]
    email_tmp = render_to_string(
        'company_registered_notification.html',
        {'domain': settings.CURRENT_SITE, 'login': email, 'password': password}
    )
    msg = EmailMultiAlternatives(subject, email_tmp, from_mail, to_list)
    msg.attach_alternative(email_tmp, "text/html")
    msg.send()
