from django.contrib import admin
from bepro_statistics.models import Statistic, StatisticObserver, UserStatistic


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'statistic_type', 'department', 'role')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    raw_id_fields = ('department', 'role')


@admin.register(StatisticObserver)
class StatisticObserverAdmin(admin.ModelAdmin):
    list_display = ('id', 'statistic', 'role')


@admin.register(UserStatistic)
class UserStatisticAdmin(admin.ModelAdmin):
    list_display = ('id', 'statistic', 'role', 'day', 'fact')
    raw_id_fields = ('statistic', 'role')
