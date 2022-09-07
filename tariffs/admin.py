from django.contrib import admin

from tariffs.models import Tariff, TestPrice


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_employees_qty', 'month_price', 'year_price')


@admin.register(TestPrice)
class TestPriceAdmin(admin.ModelAdmin):
    list_display = ('test_one_price', 'test_three_price')

