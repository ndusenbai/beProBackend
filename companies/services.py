from django.apps import apps
from django.db.transaction import atomic
from django.db.models import Count, Prefetch
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet

from auth_user.services import create_employee_schedules
from companies.models import Department, Company, Role, RoleChoices
from timesheet.models import DepartmentSchedule

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
    hr_department = Department.objects.create(
        name='HR',
        is_hr=True,
        company=company,
    )
    department_schedule = [
        DepartmentSchedule(department=hr_department, week_day=i, time_from='09:00', time_to='18:00') for i in range(0, 5)
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
        latitude=data['latitude'],
        longitude=data['longitude'],
        head_of_department=head_of_department,
    )
    bulk_create_department_schedules(department, schedules)
    if data['head_of_department']:
        title = data['head_of_department'].pop('title')
        grade = data['head_of_department'].pop('grade')
        head_of_department = User.objects.create_user(**data['head_of_department'])
        create_employee_schedules(head_of_department, schedules, user.selected_company)
        Role.objects.create(
            company=user.selected_company,
            department=department,
            role=RoleChoices.HEAD_OF_DEPARTMENT,
            user=head_of_department,
            title=title,
            grade=grade,
        )
        department.head_of_department = head_of_department
        department.save()


@atomic
def update_department(instance: Department, data) -> None:
    DepartmentSchedule.objects.filter(department=instance).delete()
    bulk_create_department_schedules(instance, data.pop('schedules'))
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


def get_department_list(company):
    return apps.get_model(
        app_label='companies',
        model_name='Department'
    ).objects.filter(company=company)


def get_departments_qs() -> QuerySet[Department]:
    return Department.objects.filter(company__is_deleted=False)\
        .annotate(employees_count=Count('roles')) \
        .prefetch_related(Prefetch('department_schedules', to_attr='schedules'))


def get_company_qs() -> QuerySet[Company]:
    return Company.objects.filter(is_deleted=False)\
        .annotate(employees_count=Count('roles'))
