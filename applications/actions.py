from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from applications.models import ApplicationToCreateCompany, ApplicationStatus

User = get_user_model()


def set_status_new(modeladmin, request, queryset):
    with atomic():
        for obj in queryset:
            User.objects.filter(email=obj.email).delete()
            ApplicationToCreateCompany.objects.filter(id=obj.id).update(status=ApplicationStatus.NEW)
