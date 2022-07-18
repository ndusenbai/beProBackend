from rest_framework.permissions import BasePermission

from companies.models import RoleChoices


class StatisticsPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.role.role == RoleChoices.HR:
            return True
        return False
