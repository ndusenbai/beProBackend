from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class CompanyAlreadyExists(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Компания с таким названием уже существует')
    default_code = 'company-already-exists'
