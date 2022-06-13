from django.contrib import admin
from auth_user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'is_active')
    list_display_links = ('id', 'email', 'full_name')
    list_filter = ('is_active', 'is_superuser')
