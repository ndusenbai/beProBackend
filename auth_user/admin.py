from django.contrib import admin
from auth_user.models import User, AcceptCode
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('id', 'email', 'full_name', 'is_active')
    list_display_links = ('id', 'email', 'full_name')
    list_filter = ('is_active', 'is_superuser')
    raw_id_fields = ('selected_company',)
    search_fields = ('id', 'email', 'last_name', 'first_name', 'middle_name')

    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
            "fields": ("first_name", "last_name", "middle_name", "phone_number", "avatar", "selected_company")
        }),
        (
            _("Permissions"),
            {
                "fields": (
                    "assistant_type",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_admin",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ('created_at', 'last_login', )


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
