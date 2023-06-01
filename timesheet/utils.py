from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class EmployeeTooFarFromDepartment(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Вы не находитесь в радиусе вашего отдела')
    default_code = 'too_far'


class FillUserStatistic(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Заполните статистику')
    default_code = 'fill_statistics'


class CheckInAlreadyExistsException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Сначала сделайте check out')
    default_code = 'make_check_out'


class TooEarlyCheckoutException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Еще рано до check out')
    default_code = 'too_early'


class EmailExistsException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Уже есть пользователь с такой почтой')
    default_code = 'email_exists'


class TookOffException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Вы сегодня отпросились')
    default_code = 'today_took_off'


class CheckOutFirstException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Сделайте чекаут')
    default_code = 'make_check_out_first'
