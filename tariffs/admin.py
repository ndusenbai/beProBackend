from django.contrib import admin

from tariffs.models import Tariff


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_employees_qty', 'month_price', 'year_price')
