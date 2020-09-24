from rest_framework.permissions import BasePermission


class IsNotAuth(BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin'
        else:
            return False


class HasDetailPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('DELETE', 'PUT', 'PATCH'):
            return (request.user.role == "moderator"
                    or request.user.role == "admin"
                    or request.user.id == obj.author_id)
        return True
