from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.apps import apps


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

