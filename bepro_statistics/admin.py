from django.contrib import admin
from bepro_statistics.models import Statistic, StatisticObserver, UserStatistic


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'statistic_type', 'user')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(StatisticObserver)
class StatisticObserverAdmin(admin.ModelAdmin):
    list_display = ('id', 'statistic', 'user')


@admin.register(UserStatistic)
class UserStatisticAdmin(admin.ModelAdmin):
    list_display = ('id', 'statistic', 'user', 'weekday', 'fact')
