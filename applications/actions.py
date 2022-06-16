from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from applications.models import ApplicationToCreateCompany, ApplicationStatus
from companies.models import Role, RoleChoices

User = get_user_model()


def set_app_to_create_company_status_new(modeladmin, request, queryset):
    with atomic():
        for obj in queryset:
            Role.objects.get(user__email=obj.email, role=RoleChoices.OWNER).company.delete()
            User.objects.filter(email=obj.email).delete()
            ApplicationToCreateCompany.objects.filter(id=obj.id).update(status=ApplicationStatus.NEW)
