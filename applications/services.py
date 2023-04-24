from typing import Tuple, OrderedDict
from datetime import date
from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.transaction import atomic
from django.http import HttpRequest
from django.utils import timezone

from auth_user.services import get_domain
from auth_user.tasks import send_created_account_notification
from applications.models import ApplicationToCreateCompany, ApplicationStatus, TariffApplication, TestApplication
from auth_user.utils import UserAlreadyExists
from companies.models import Company, Department, CompanyService
from companies.utils import CompanyAlreadyExists
from scores.models import Reason
from tariffs.models import TariffPeriod
from timesheet.models import DepartmentSchedule

User = get_user_model()


def update_application_to_create_company(instance: ApplicationToCreateCompany, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def update_tariff_application(instance: TariffApplication, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def update_test_application(instance: TestApplication, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


@atomic
def accept_application_to_create_company(request: HttpRequest, instance: ApplicationToCreateCompany) -> None:
    company, hr_department = create_company_and_hr_department(instance)
    owner, password = create_owner(instance, company)
    company.owner = owner
    company.save()
    create_tariff_application(instance, owner)
    enable_services_for_company(company)
    update_application_to_create_company(instance, {'status': ApplicationStatus.ACCEPTED})
    domain = get_domain(request)
    email = owner.email
    send_created_account_notification.delay(domain, email, password)


def create_tariff_application(instance: ApplicationToCreateCompany, owner: User):
    start_date = date.today()
    if instance.period == TariffPeriod.MONTHLY:
        end_date = start_date + relativedelta(months=1)
    elif instance.period == TariffPeriod.YEARLY:
        end_date = start_date + relativedelta(years=1)

    TariffApplication.objects.create(
        tariff_id=instance.tariff_id,
        owner=owner,
        start_date=start_date,
        end_date=end_date,
        period=instance.period,
        status=ApplicationStatus.ACCEPTED,
    )


def enable_services_for_company(company: Company):
    CompanyService.objects.create(company=company)


def create_company_and_hr_department(instance: ApplicationToCreateCompany) -> Tuple[Company, Department]:
    try:
        company = Company.objects.create(
            name=instance.company_name,
            legal_name=instance.company_legal_name,
            years_of_work=instance.years_of_work,
            max_employees_qty=instance.max_employees_qty,
        )
    except IntegrityError:
        raise CompanyAlreadyExists()
    Reason.objects.create(name='Опоздание', score=-10, is_auto=True, company=company)
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
    try:
        owner = User.objects.create(
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            middle_name=instance.middle_name,
            phone_number=instance.phone_number,
            selected_company=company,
        )
    except IntegrityError:
        raise UserAlreadyExists()
    password = User.objects.make_random_password()
    owner.set_password(password)
    owner.save(update_fields=['password'])
    return owner, password


@atomic
def approve_tariff_application(tariff_app: TariffApplication) -> None:
    if tariff_app.is_instant_apply:
        start_date = timezone.now().date()
        end_date = None
        if tariff_app.period == TariffPeriod.MONTHLY:
            end_date = start_date + relativedelta(months=1)
        elif tariff_app.period == TariffPeriod.YEARLY:
            end_date = start_date + relativedelta(years=1)

        tariff_app.start_date = start_date
        tariff_app.end_date = end_date
        TariffApplication.objects.filter(
            owner=tariff_app.owner,
            status=ApplicationStatus.ACCEPTED,
            end_date__gte=start_date,
        ).exclude(id=tariff_app.id).update(status=ApplicationStatus.CANCELED)

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


def change_status_of_tariff_application(instance: TariffApplication, application_status: int) -> None:
    if application_status == ApplicationStatus.ACCEPTED:
        approve_tariff_application(instance)
    elif application_status == ApplicationStatus.DECLINED:
        update_tariff_application(instance, {'status': application_status})


def change_status_of_test_application(instance: TestApplication, application_status: int) -> None:
    if application_status == ApplicationStatus.ACCEPTED:
        update_test_application(instance, {'status': application_status})
    elif application_status == ApplicationStatus.DECLINED:
        update_test_application(instance, {'status': application_status})


def check_email_existence(email):
    if User.objects.filter(email=email).exists():
        raise ValueError('Уже есть пользователь с такой почтой')
