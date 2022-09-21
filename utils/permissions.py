from django.apps import apps
from rest_framework.permissions import BasePermission, SAFE_METHODS

from auth_user.services import get_user_role
from companies.models import Role, RoleChoices


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

        if role == 'superuser':
            return True

        if view.action in {'retrieve', 'get', 'list'}:

            if view.action == 'list':
                if not request.GET.get('company'):
                    return False
                else:
                    if role not in {"owner", "superuser", "observer"} and int(request.GET.get('company')) == request.user.role.department.company_id:
                        return True
            if view.action == 'retrieve':
                if role not in {"owner", "superuser"} and int(view.kwargs['pk']) == request.user.role.department_id:
                    return True

            if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr', 'observer'}):
                return True

        else:
            if request.user.is_authenticated and (role in {'owner', 'superuser', 'hr'}):
                return True

        return False


class EmployeesPermissions(BasePermission):
    def has_permission(self, request, view):
        role = get_user_role(request.user)

        if role == 'superuser':
            return True

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
        if not request.user.is_authenticated:
            return False

        role = get_user_role(request.user)

        if request.user.is_authenticated and role == 'superuser':
            return True
        if view.action == 'list':
            score_user_company_id = Role.objects.get(id=request.GET['role']).company_id
            if request.user.selected_company_id == score_user_company_id:
                return True
        elif view.action in ['create', 'destroy']:
            if role in ['hr', 'owner']:
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


class SuperuserOrOwnerOrHRPermission(BasePermission):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        role = get_user_role(request.user)

        if role in {'superuser', 'owner', 'hr'}:
            return True

        return False


class IsStaffPermission(BasePermission):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.is_staff:
            return True

        return False


class TestPricePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        is_staff = IsStaffPermission().has_permission(request, view)
        is_owner_or_hr = SuperuserOrOwnerOrHRPermission().has_permission(request, view)
        if is_staff or is_owner_or_hr:
            return True

        return False


class TestApplicationPermission(BasePermission):
    def has_permission(self, request, view):
        is_staff = IsStaffPermission().has_permission(request, view)
        if is_staff:
            return True

        if view.action == 'list':
            is_owner_or_hr = SuperuserOrOwnerOrHRPermission().has_permission(request, view)
            if is_owner_or_hr:
                return True

        return False


class TariffApplicationPermission(BasePermission):
    def has_permission(self, request, view):
        is_staff = IsStaffPermission().has_permission(request, view)
        if is_staff:
            return True

        if view.action == 'list':
            is_owner_or_hr = SuperuserOrOwnerOrHRPermission().has_permission(request, view)
            if is_owner_or_hr:
                return True

        return False


class CompanyServicePermission(BasePermission):
    def has_permission(self, request, view):
        permission = SuperuserOrOwnerOrHRPermission().has_permission(request, view)
        if permission:
            return True

        is_observer = Role.objects.filter(
            company=request.user.selected_company,
            role=RoleChoices.OBSERVER,
            user=request.user).exists()

        if is_observer:
            return True

        return False
