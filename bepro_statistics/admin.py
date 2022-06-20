from django.contrib import admin
from bepro_statistics.models import Statistic, StatisticObserver


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'statistic_type', 'company')
    search_fields = ('name', 'company__name')


@admin.register(StatisticObserver)
class StatisticObserverAdmin(admin.ModelAdmin):
    list_display = ('id', 'statistic', 'user')
