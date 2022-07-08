from django.contrib import admin
from scores.models import Reason, Score


@admin.register(Reason)
class ReasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'score', 'is_auto', 'company')
    search_fields = ('name', 'company')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'reason')
    list_display_links = ('id', 'role', 'reason')
    raw_id_fields = ('role', 'reason')
