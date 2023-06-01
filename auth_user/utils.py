from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class UserAlreadyExists(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Пользователь с данной электронной почтой уже зарегистрирован в системе')
    default_code = 'user-already-exists'
