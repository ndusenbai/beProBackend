from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.apps import apps

from auth_user.services import get_user_role


def check_hr_of_company(user):
    if not user.is_authenticated:
        return False

    return apps.get_model(app_label='companies', model_name='role').objects.filter(
        user=user,
        role=2
    ).exists()


def check_head_of_department(user):
    if not user.is_authenticated:
        return False

    return apps.get_model(app_label='companies', model_name='role').objects.filter(
        user=user,
        role=5
    ).exists()


class IsHumanResourceUser(BasePermission):
    # def has_object_permission(self, request, view, obj):
    #     if request.method in SAFE_METHODS:
    #         return True
    #     return check_hr_of_company(request.user)

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return check_hr_of_company(request.user)


class IsHeadOfDepartment(BasePermission):
    # def has_object_permission(self, request, view, obj):
    #     if request.method in SAFE_METHODS:
    #         return True
    #     return check_head_of_department(request.user)

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return check_head_of_department(request.user)


class IsAssistantMarketingOrSuperuser(BasePermission):
    def has_permission(self, request, view):

        if view.action == 'create':
            return True

        role = get_user_role(request.user)

        if view.action in {'get', 'list', 'retrieve', 'update', 'partial_update', 'destroy'} and role in {'admin_marketing', 'superuser'}:
            return True

        return False


class IsAssistantProductOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if request.user.is_authenticated and (role == 'admin_production_worker' or role == 'superuser'):
            return True
        return False


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if request.user.is_authenticated and role == 'owner':
            return True
        return False


class IsOwnerOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if request.user.is_authenticated and (role == 'owner' or role == 'superuser'):
            return True
        return False


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if request.user.is_authenticated and role == 'superuser':
            return True
        return False


class CompanyPermissions(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if view.action in {'retrieve', 'get', 'list'}:
            if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr',  'observer'}):
                return True
        else:
            if request.user.is_authenticated and (role in {'owner', 'superuser'}):
                return True
        return False


class DepartamentPermissions(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)

        if view.action in {'retrieve', 'get', 'list'}:

            if view.action == 'list':
                if not request.GET.get('company'):
                    return False

            if request.user.is_authenticated and (role in {'owner', 'employee', 'superuser', 'hr', 'observer'}):
                return True

        else:
            if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr'}):
                return True

        return False


class EmployeesPermissions(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if view.action in {'retrieve', 'get', 'list'}:

            if view.action == 'list':
                if not request.GET.get('company'):
                    return False

            if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr', 'observer', 'employee', 'head_of_department'}):
                return True
        else:
            if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr'}):
                return True

        return False


class StatisticPermissions(BasePermission):

    def has_permission(self, request, view):
        role = get_user_role(request.user)

        if view.action in {'retrieve', 'get', 'list'}:

            if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr', 'observer', 'employee', 'head_of_department'}):
                return True
        else:
            if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr'}):
                return True

        return False


class HistoryStatisticPermissions(BasePermission):

    def has_permission(self, request, view):
        role = get_user_role(request.user)

        if not request.GET.get('role_id'):
            return False

        if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr', 'observer'}):
            return True

        return False


class ReasonPermissions(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)

        if view.action == 'list':
            if not request.GET.get('company'):
                return False

        if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr'}):
            return True

        return False


class MonthScorePermissions(BasePermission):

    def has_permission(self, request, view):
        if not request.GET.get('role'):
            return False

        if not request.user.is_authenticated:
            return False

        return True


class TimeSheetPermissions(BasePermission):

    def has_permission(self, request, view):
        if not request.GET.get('role_id'):
            return False

        if not request.user.is_authenticated:
            return False

        role = get_user_role(request.user)

        if view.action in ('partial_update', 'update') and role in ('employees', 'observer'):
            return False

        return True


class ChangeTimeSheetPermissions(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        role = get_user_role(request.user)

        if view.action in ('partial_update', 'update') and role in ('employees', 'observer'):
            return False

        return True


class StatisticsPermission(BasePermission):

    def has_permission(self, request, view):

        role = get_user_role(request.user)

        if request.user.is_authenticated and role in {'superuser', 'owner', 'hr'}:
            return True
        return False


class ObserverPermission(BasePermission):

    def has_permission(self, request, view):

        role = get_user_role(request.user)

        if request.user.is_authenticated and role in {'superuser', 'owner'}:
            return True
        return False


class ScorePermission(BasePermission):

    def has_permission(self, request, view):

        role = get_user_role(request.user)

        if request.user.is_authenticated and role in {'superuser', 'owner', 'hr'}:
            return True
        return False


class CheckPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        role = get_user_role(request.user)

        if role in {'owner', 'observer', 'hr', 'employee', 'head_of_department'}:
            return True

        return False
