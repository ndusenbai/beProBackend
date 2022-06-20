from datetime import time
from django.apps import apps
from companies.models import DepartmentSchedule, EmployeeSchedule


def update_department_schedule(instance: DepartmentSchedule, time_from: time, time_to: time) -> None:
    instance.time_from = time_from
    instance.time_to = time_to
    instance.save()


def update_employee_schedule(instance: EmployeeSchedule, time_from: time, time_to: time) -> None:
    instance.time_from = time_from
    instance.time_to = time_to
    instance.save()


def get_department_list(company):
    return apps.get_model(
        app_label='companies',
        model_name='Department'
    ).objects.filter(company=company)
