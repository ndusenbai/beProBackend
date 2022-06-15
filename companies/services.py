from companies.models import Schedule


def update_schedule(instance: Schedule, time_from, time_to) -> None:
    instance.time_from = time_from
    instance.time_to = time_to
    instance.save()
