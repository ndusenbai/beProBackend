from django.db.transaction import atomic

from applications.models import ApplicationToCreateCompany, ApplicationStatus


def update_application_to_create_company(instance: ApplicationToCreateCompany, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def accept_application_to_create_company(instance: ApplicationToCreateCompany) -> None:
    with atomic():
        update_application_to_create_company(instance, {'status': ApplicationStatus.ACCEPTED})
        # TODO: create company, owner user and hr department
        pass
