from django.apps import apps
from django.db.transaction import atomic
from django.contrib.auth import get_user_model

from companies.models import Department, Company, Role, RoleChoices
from timesheet.models import DepartmentSchedule

User = get_user_model()


@atomic()
def create_company(user: User, data) -> None:
    company = Company.objects.create(
        name=data['name'],
        legal_name=data['legal_name'],
        years_of_work=data['years_of_work'],
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

    Role.objects.create(
        company=company,
        department=None,
        role=RoleChoices.OWNER,
        user=user,
        title='Владелец',
        grade=4,
    )


def update_department(instance: Department, data) -> None:
    with atomic():
        schedules = data.pop('schedules')
        DepartmentSchedule.objects.filter(department=instance).delete()
        new_schedules = [
            DepartmentSchedule(
                department=instance,
                week_day=schedule['week_day'],
                time_from=schedule['time_from'],
                time_to=schedule['time_to'],
            ) for schedule in schedules]
        DepartmentSchedule.objects.bulk_create(new_schedules)

        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()


def get_department_list(company):
    return apps.get_model(
        app_label='companies',
        model_name='Department'
    ).objects.filter(company=company)
