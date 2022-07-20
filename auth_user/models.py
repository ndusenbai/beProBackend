from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.timezone import now
from datetime import timedelta
import random

from utils.models import BaseModel
from utils.tools import log_exception


class UserManager(BaseUserManager):

    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = email.lower()
        user = self.model(email=email, **extra_fields)
        password = self.model.objects.make_random_password()
        user.set_password(password)
        user.save()
        user.send_mail_invitation(password)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        email = email.lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class AssistantTypes(models.IntegerChoices):
    NON_ASSISTANT = 0, _('Non assistant')
    MARKETING = 1, _('Marketing-sales')
    PRODUCTION_WORKERS = 2, _('Production workers')


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=70, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assistant_type = models.PositiveSmallIntegerField(
        choices=AssistantTypes.choices,
        default=AssistantTypes.NON_ASSISTANT,
        blank=True
    )
    selected_company = models.ForeignKey(to='companies.Company', on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'

    @property
    def full_name(self):
        first_name = self.first_name if self.first_name else ''
        last_name = self.last_name if self.last_name else ''
        middle_name = self.middle_name if self.middle_name else ''
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        return full_name if len(full_name) > 0 else 'Данные не заполнены!'

    objects = UserManager()

    def send_mail_invitation(self, password: str) -> None:
        try:
            subject = 'Добро пожаловать!'
            from_mail = settings.EMAIL_HOST_USER
            to_list = [self.email, ]
            email_tmp = render_to_string(
                'company_registered_notification.html',
                {'domain': settings.CURRENT_SITE, 'login': self.email, 'password': password}
            )
            msg = EmailMultiAlternatives(subject, email_tmp, from_mail, to_list)
            msg.attach_alternative(email_tmp, "text/html")
            msg.send()
        except Exception as e:
            log_exception(e, 'Error in send_mail_invitation')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class AcceptCode(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pin_codes")
    code = models.PositiveIntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)], blank=True)
    expiration = models.DateTimeField(blank=True, editable=False)
    is_accepted = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}, Code: {self.code}, Accepted: {self.is_accepted}"

    def set_accept_code(self):
        self.code = random.randint(1000, 9999)

    def save(self, *args, **kwargs):
        if not self.code:
            self.expiration = now() + timedelta(days=1)
            self.set_accept_code()
        super(AcceptCode, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['code', 'is_accepted']
        verbose_name = "Код для восстановления пароля"
        verbose_name_plural = "Коды для восстановления пароля"
