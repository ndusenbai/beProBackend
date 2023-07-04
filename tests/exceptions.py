from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class VersionAlreadyExists(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Данный пользователь уже сдавал вариант этого теста')
    default_code = 'version-already-exists'


class TestAlreadyFinished(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Тест уже пройден и не может быть сдан повторно')
    default_code = 'test-already-finished'


class NoEmailTestException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Невозможно отправить приглашение, т.к. не указана электронная почта')
    default_code = 'no-email-test'


class TestAlreadyFinishedEmailException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Невозможно отправить приглашение, т.к. тест уже пройден')
    default_code = 'test-already-finished-email'


class NoPaidTestException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Необходимо сначала оплатить тест')
    default_code = 'no-paid-tests'
