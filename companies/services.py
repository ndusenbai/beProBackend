from typing import OrderedDict

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, F
from django.db.models.query import QuerySet
from django.db.transaction import atomic
from rest_framework import status

from auth_user.services import User
from companies.models import Department, Company, Role, RoleChoices, CompanyService, Zone
from scores.models import Reason
from scores.utils import GetScoreForRole
from timesheet.models import DepartmentSchedule, EmployeeSchedule

User = get_user_model()


@atomic()
def create_company(user: User, data) -> None:
    company = Company.objects.create(
        name=data['name'],
        legal_name=data['legal_name'],
        years_of_work=data['years_of_work'],
        max_employees_qty=data['max_employees_qty'],
        owner=user,
    )
    CompanyService.objects.create(company=company)
    Reason.objects.create(name='Опоздание', score=-10, is_auto=True, company=company)
    hr_department = Department.objects.create(
        name='HR',
        is_hr=True,
        company=company,
        timezone=data.get('timezone', '+06:00')
    )
    department_schedule = [
        DepartmentSchedule(department=hr_department, week_day=i, time_from='09:00', time_to='18:00')
        for i in range(0, 5)
    ]
    DepartmentSchedule.objects.bulk_create(department_schedule)


def update_company(instance: Company, data: dict) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


@atomic
def create_department(user: User, data: dict) -> None:
    head_of_department = None
    schedules = data.pop('schedules')
    department = Department.objects.create(
        name=data['name'],
        company=user.selected_company,
        address=data['address'],
        is_manual_address=data['is_manual_address'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        radius=data['radius'],
        head_of_department=head_of_department,
        timezone=data.get('timezone', '+06:00')
    )
    bulk_create_department_schedules(department, schedules)
    if data['head_of_department']:
        title = data['head_of_department'].pop('title')
        grade = data['head_of_department'].pop('grade')
        try:
            head_of_department_user = User.objects.get(email=data['head_of_department']['email'])
        except User.DoesNotExist:
            data['head_of_department']['selected_company_id'] = department.company_id
            head_of_department_user = User.objects.create_user(**data['head_of_department'])
        head_of_department_role = Role.objects.create(
            company=user.selected_company,
            department=department,
            role=RoleChoices.HEAD_OF_DEPARTMENT,
            user=head_of_department_user,
            title=title,
            grade=grade,
        )
        create_employee_schedules(head_of_department_role, schedules)
        department.head_of_department = head_of_department_role
        department.save()


@atomic
def update_department(instance: Department, data) -> None:
    DepartmentSchedule.objects.filter(department=instance).delete()
    bulk_create_department_schedules(instance, data.pop('schedules'))

    head_of_department_changed = data['head_of_department_id'] is not None and \
                                 data['head_of_department_id'] != instance.head_of_department_id

    if head_of_department_changed:
        Role.objects.filter(id=data['head_of_department_id']).update(role=RoleChoices.HEAD_OF_DEPARTMENT)
        if instance.head_of_department_id:
            if instance.is_hr:
                Role.objects.filter(id=instance.head_of_department_id).update(role=RoleChoices.HR)
            else:
                Role.objects.filter(id=instance.head_of_department_id).update(role=RoleChoices.EMPLOYEE)

    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()


def bulk_create_department_schedules(department: Department, schedules: list) -> None:
    new_schedules = [
        DepartmentSchedule(
            department=department,
            week_day=schedule['week_day'],
            time_from=schedule['time_from'],
            time_to=schedule['time_to'],
        ) for schedule in schedules]
    DepartmentSchedule.objects.bulk_create(new_schedules)


def get_departments_qs() -> QuerySet[Department]:
    return Department.objects.filter(
        company__is_deleted=False
    ).annotate(
        employees_count=Count('roles')
    ).prefetch_related(
        Prefetch(
            'department_schedules',
            queryset=DepartmentSchedule.objects.order_by().select_related(
                'department',
            ).annotate(
                timezone=F('department__timezone')
            ),
            to_attr='schedules'
        )
    ).order_by('id')


def get_company_qs() -> QuerySet[Company]:
    return Company.objects.filter(is_deleted=False) \
        .annotate(employees_count=Count('roles')).order_by('id')


def get_employee_list():
    return Role.objects.exclude(
        role=RoleChoices.OBSERVER
    ).annotate(
        score=GetScoreForRole('companies_role.id')
    ).prefetch_related(
        Prefetch(
            'employee_schedules',
            queryset=EmployeeSchedule.objects.order_by().select_related(
                'role', 'role__department'
            ).annotate(
                timezone=F('role__department__timezone')
            ),
            to_attr='schedules'
        )
    ).distinct()


@atomic
def create_employee(data: dict) -> None:
    title = data.pop('title')
    grade = data.pop('grade')
    department_id = data.pop('department_id')
    schedules = data.pop('schedules')

    department = Department.objects.get(id=department_id)
    data['selected_company_id'] = department.company_id

    if department.company.is_active:
        try:
            employee = User.objects.get(email=data['email'])
            User.objects.filter(email=data['email']).update(
                first_name=data['first_name'],
                last_name=data['last_name'],
                middle_name=data['middle_name'],
            )
        except User.DoesNotExist:
            employee = User.objects.create_user(**data)
        role = Role.objects.create(
            company=department.company,
            department=department,
            role=RoleChoices.HR if department.is_hr else RoleChoices.EMPLOYEE,
            user=employee,
            title=title,
            grade=grade
        )
        create_employee_schedules(role, schedules)
    else:
        raise Exception({'message': 'Тариф компании истек. Необходимо обновить тариф', 'status': 400})


@atomic
def update_employee(role: Role, data: dict) -> None:
    data.pop('email', None)
    schedules = data.pop('schedules')
    role_data = {
        'title': data.pop('title'),
        'grade': data.pop('grade'),
        'department_id': data.pop('department_id'),
    }

    Role.objects.filter(id=role.id).update(**role_data)
    update_employee_schedules(role, schedules)

    user = role.user

    for key, value in data.items():
        setattr(user, key, value)
    user.save()


def update_employee_schedules(role: Role, schedules):
    EmployeeSchedule.objects.filter(role=role).delete()
    create_employee_schedules(role, schedules)


def create_employee_schedules(role: Role, schedules: list) -> None:
    new_schedules = [
        EmployeeSchedule(
            role=role,
            week_day=schedule['week_day'],
            time_from=schedule['time_from'],
            time_to=schedule['time_to'],
        ) for schedule in schedules]
    EmployeeSchedule.objects.bulk_create(new_schedules)


def delete_head_of_department_role(instance: Department) -> None:
    Role.objects.filter(user=instance.head_of_department).delete()


def update_observer(instance: Role, data: OrderedDict):
    user = instance.user

    for key, value in data.items():
        setattr(user, key, value)
    user.save()


@atomic
def create_observer_and_role(data: OrderedDict):
    try:
        observer = User.objects.get(email=data['email'])
    except User.DoesNotExist:
        observer = User.objects.create_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=data['middle_name'],
            email=data['email'],
            selected_company=data['company']
        )
    if Role.objects.filter(user=observer).exists():
        return {'message': 'observer with this email is already created'}, status.HTTP_400_BAD_REQUEST

    Role.objects.create(
        company=data['company'],
        department=None,
        role=RoleChoices.OBSERVER,
        user=observer
    )

    return {'message': 'created'}, status.HTTP_201_CREATED


def get_observers_qs(owner):
    if owner.id:
        owner_companies = Company.objects.filter(owner=owner).values_list('id', flat=True)
        return Role.objects.filter(role=RoleChoices.OBSERVER, company_id__in=owner_companies)

    return Role.objects.none()


def update_company_services(data: dict) -> None:
    for company_service in data['company_services']:
        instance = CompanyService.objects.get(id=company_service.pop('id'))
        for key, value in company_service.items():
            setattr(instance, key, value)
        instance.save()


def get_qs_retrieve_company_services():
    return Company.objects.all().annotate(
        analytics_enabled=F('service__analytics_enabled'),
        time_tracking_enabled=F('service__time_tracking_enabled'),
        tests_enabled=F('service__tests_enabled'),
    )


def get_zones_qs(user):
    return Zone.objects.filter(
        company=user.role.company
    )
