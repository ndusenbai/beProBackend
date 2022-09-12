from django.dispatch import receiver
from django.db.models.signals import post_save

from applications.models import TariffApplication, ApplicationStatus
from companies.models import Role, Company, RoleChoices
from utils.tools import log_exception


@receiver(post_save, sender=Role)
def check_employees_qty(sender, instance, created, **kwargs):
    try:
        if not created:
            return True
        if not instance.company.is_active:
            raise Exception({'message': 'Тариф компании истек. Необходимо обновить тариф.', 'status': 400})

        check_employees_qty_in_company(instance)
        check_employees_qty_in_tariff(instance)
    except Exception as e:
        log_exception(e)
        raise e


def check_employees_qty_in_company(role):
    max_employees_qty = role.company.max_employees_qty
    employees_count = Role.objects.filter(company=role.company).count()
    if employees_count > max_employees_qty:
        role.delete()
        raise Exception('Слишком много сотрудников в компании')


def check_employees_qty_in_tariff(role):
    owner = role.company.owner
    tariff_application = TariffApplication.objects \
        .filter(status=ApplicationStatus.ACCEPTED, owner=owner).order_by('-end_date').first()
    if not tariff_application:
        raise Exception('Создайте заявку на продление для компании')
    max_employees_qty = tariff_application.tariff.max_employees_qty

    owner_companies = Company.objects.filter(owner=owner).values_list('id', flat=True)
    employees_count = Role.objects.filter(company__in=owner_companies).count()
    if employees_count > max_employees_qty:
        role.delete()
        raise Exception('Сотрудников больше, чем допустимо тарифом')
