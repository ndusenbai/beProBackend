from django.dispatch import receiver
from django.db.models.signals import pre_save

from applications.models import TariffApplication, ApplicationStatus
from companies.models import Role, Company, RoleChoices
from utils.tools import log_exception


@receiver(pre_save, sender=Role)
def check_employees_qty(sender, instance, **kwargs):
    try:
        if not instance.company.is_active:
            raise Exception('Company is not active. Need to renew tariff')
        check_employees_qty_in_company(instance)
        check_employees_qty_in_tariff(instance)
    except Exception as e:
        log_exception(e)
        raise e


def check_employees_qty_in_company(role):
    max_employees_qty = role.company.max_employees_qty
    employees_count = Role.objects.filter(company=role.company).exclude(role=RoleChoices.OWNER).count()
    if employees_count >= max_employees_qty:
        raise Exception('Too many employees in company')


def check_employees_qty_in_tariff(role):
    owner = role.company.owner
    tariff_application = TariffApplication.objects \
        .filter(status=ApplicationStatus.ACCEPTED, owner=owner).order_by('-end_date').first()
    max_employees_qty = tariff_application.tariff.max_employees_qty

    owner_companies = Company.objects.filter(owner=owner).values_list('id', flat=True)
    employees_count = Role.objects.filter(company__in=owner_companies).exclude(role=RoleChoices.OWNER).count()
    if employees_count >= max_employees_qty:
        raise Exception('Too many employees for tariff')
