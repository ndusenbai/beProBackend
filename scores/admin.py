from django.contrib import admin
from scores.models import Reason, Score
from modeltranslation.admin import TranslationAdmin


@admin.register(Reason)
class ReasonAdmin(TranslationAdmin):
    list_display = ('id', 'name_ru', 'score', 'is_auto', 'company')
    raw_id_fields = ('company',)
    search_fields = ('name_ru', 'company')



@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'role_id', 'name', 'points', 'created_at', 'updated_at')
    list_display_links = ('id', 'role')
    raw_id_fields = ('role', 'created_by')
    search_fields = ('role__user__email',)
    date_hierarchy = 'created_at'
