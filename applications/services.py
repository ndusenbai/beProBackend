from typing import Tuple, OrderedDict

from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from django.http import HttpRequest

from auth_user.services import get_domain
from auth_user.tasks import send_created_account_notification
from applications.models import ApplicationToCreateCompany, ApplicationStatus, TariffApplication
from companies.models import Company, Department, Role, RoleChoices
from timesheet.models import DepartmentSchedule

User = get_user_model()


def update_application_to_create_company(instance: ApplicationToCreateCompany, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


@atomic
def accept_application_to_create_company(request: HttpRequest, instance: ApplicationToCreateCompany) -> None:
    company, hr_department = create_company_and_hr_department(instance)
    owner, password = create_owner(instance, company)
    company.owner = owner
    company.save()
    update_application_to_create_company(instance, {'status': ApplicationStatus.ACCEPTED})
    domain = get_domain(request)
    email = owner.email
    send_created_account_notification.delay(domain, email, password)


def create_company_and_hr_department(instance: ApplicationToCreateCompany) -> Tuple[Company, Department]:
    company = Company.objects.create(
        name=instance.company_name,
        legal_name=instance.company_legal_name,
        years_of_work=instance.years_of_work,
        max_employees_qty=instance.max_employees_qty,
    )
    hr_department = Department.objects.create(
        name='HR',
        is_hr=True,
        company=company,
    )
    department_schedule = [
        DepartmentSchedule(department=hr_department, week_day=i, time_from='09:00', time_to='18:00') for i in range(0, 5)
    ]
    DepartmentSchedule.objects.bulk_create(department_schedule)
    return company, hr_department


def create_owner(instance: ApplicationToCreateCompany, company: Company) -> Tuple[User, str]:
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
    return owner, password


@atomic
def approve_tariff_application(application_id: int) -> None:
    tariff_app = TariffApplication.objects.get(id=application_id)
    if tariff_app.status != ApplicationStatus.NEW:
        raise Exception('Application must be in NEW status')
    Company.objects.filter(owner=tariff_app.owner).update(is_active=True)
    tariff_app.status = ApplicationStatus.ACCEPTED
    tariff_app.save()


def change_status_of_application_to_create_company(
        request: HttpRequest,
        instance: ApplicationToCreateCompany,
        data: OrderedDict) -> None:
    application_status = data['status']
    if application_status == ApplicationStatus.ACCEPTED:
        accept_application_to_create_company(request, instance)
    elif application_status == ApplicationStatus.DECLINED:
        update_application_to_create_company(instance, {'status': application_status})
