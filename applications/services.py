from typing import Tuple

from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from auth_user.services import send_created_account_notification
from applications.models import ApplicationToCreateCompany, ApplicationStatus
from companies.models import Company, Department, Role, RoleChoices, Schedule, WeekDayChoices

User = get_user_model()


def update_application_to_create_company(instance: ApplicationToCreateCompany, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def accept_application_to_create_company(instance: ApplicationToCreateCompany) -> None:
    with atomic():
        update_application_to_create_company(instance, {'status': ApplicationStatus.ACCEPTED})
        company, hr_department = create_company_and_hr_department(instance)
        owner = create_owner_and_role(instance, company)

        send_created_account_notification(owner)


def create_company_and_hr_department(instance: ApplicationToCreateCompany) -> Tuple[Company, Department]:
    company = Company.objects.create(
        name=instance.company_name,
        legal_name=instance.company_legal_name,
        years_of_work=instance.years_of_work,
    )
    hr_department = Department.objects.create(
        name='HR',
        is_hr=True,
        company=company,
    )
    schedule = [
        Schedule(department=hr_department, week_day=i, time_from='09:00', time_to='18:00') for i in range(1, 6)
    ]
    Schedule.objects.bulk_create(schedule)
    return company, hr_department


def create_owner_and_role(instance: ApplicationToCreateCompany, company: Company) -> User:
    owner = User.objects.create(
        email=instance.email,
        first_name=instance.first_name,
        last_name=instance.last_name,
        middle_name=instance.middle_name,
        phone_number=instance.phone_number,
        selected_company=company,
    )
    Role.objects.create(company=company, department=None, role=RoleChoices.OWNER, user=owner)
    password = User.objects.make_random_password()
    owner.set_password(password)
    owner.save(update_fields=['password'])
    return owner
