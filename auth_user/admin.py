from django.contrib import admin
from auth_user.models import User, AcceptCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'is_active')
    list_display_links = ('id', 'email', 'full_name')
    list_filter = ('is_active', 'is_superuser')
    raw_id_fields = ('selected_company',)
    search_fields = ('id', 'email', 'full_name')


class AcceptCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'is_accepted', 'created_at', 'updated_at')
    list_display_links = ('id', 'user',)
    search_fields = ('id', 'code',)
    readonly_fields = ('id', 'created_at', 'updated_at',)
    ordering = ('-created_at',)
    filter_horizontal = ()
    autocomplete_fields = ('user', )
    list_filter = ('is_accepted', 'user')
    fieldsets = ()

admin.site.register(AcceptCode, AcceptCodeAdmin)
