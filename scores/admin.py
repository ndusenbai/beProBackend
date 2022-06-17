from django.contrib import admin
from scores.models import Reason, Score


@admin.register(Reason)
class ReasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'score', 'is_auto', 'company')
    search_fields = ('name', 'company')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reason')
    list_display_links = ('id', 'user', 'reason')


