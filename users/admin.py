from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from .forms import UserChangeForm, UserCreationForm


User = get_user_model()


class UserAdmin(BaseUserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'username', 'is_active', 'is_admin', 'role', 'bio', 'first_name', 'last_name')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),

        ('Permissions', {'fields': ('is_admin', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)


admin.site.unregister(Group)
