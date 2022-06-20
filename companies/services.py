from django.db.transaction import atomic

from companies.models import Department, DepartmentSchedule


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
