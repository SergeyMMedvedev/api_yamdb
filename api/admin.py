from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models
from .forms import UserChangeForm, UserCreationForm


MyUser = models.User


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    empty_value_display = '-пусто-'


admin.site.register(models.Category, CategoryAdmin)


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    empty_value_display = '-пусто-'


admin.site.register(models.Genre, GenreAdmin)


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category')
    empty_value_display = '-пусто-'


admin.site.register(models.Title, TitleAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'author', 'score', 'pub_date')
    empty_value_display = '-пусто-'


admin.site.register(models.Review, ReviewAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review', 'text', 'author', 'pub_date')
    empty_value_display = '-пусто-'


admin.site.register(models.Comment, CommentAdmin)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'username', 'is_active', 'is_admin', 'role', 'bio', 'first_name', 'last_name')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),

        ('Permissions', {'fields': ('is_admin', )}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
