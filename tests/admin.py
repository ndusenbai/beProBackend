from django.contrib import admin

from tests.models import Test


@admin.register(Test)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_type', 'company', 'phone_number', 'last_name', 'first_name', 'version', 'status')
    list_filter = ('test_type', 'company')
    raw_id_fields = ('company',)
