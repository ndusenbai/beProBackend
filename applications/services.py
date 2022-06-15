from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from auth_user.services import send_created_account_notification
from applications.models import ApplicationToCreateCompany, ApplicationStatus
from companies.models import Company, Department

User = get_user_model()


def update_application_to_create_company(instance: ApplicationToCreateCompany, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def accept_application_to_create_company(instance: ApplicationToCreateCompany) -> None:
    with atomic():
        update_application_to_create_company(instance, {'status': ApplicationStatus.ACCEPTED})
        company = Company.objects.create(
            name=instance.company_name,
            legal_name=instance.company_legal_name,
            years_of_work=instance.years_of_work,
        )
        Department.objects.create(
            name='HR',
            is_hr=True,
            company=company,
        )
        owner = User.objects.create(
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            middle_name=instance.middle_name,
            phone_number=instance.phone_number,
            selected_company=company,
        )
        password = User.objects.make_random_password()
        owner.set_password(password)
        owner.save(update_fields=['password'])
        send_created_account_notification(owner)
