from rest_framework.permissions import (
    BasePermission, SAFE_METHODS
)


class IsNotAuth(BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class UsersPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'DELETE' and request.path.endswith('users/me/'):
            return True
        elif request.user.is_authenticated:
            if (request.method in ['PATCH', 'GET']
                    and request.path.endswith('users/me/')):
                return True
            else:
                return request.user.role == 'admin'
        else:
            return False


class IsAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('DELETE', 'PUT', 'PATCH'):
            if request.user.is_authenticated:
                return request.user.role == 'admin'
        else:
            return True

    def has_permission(self, request, view):
        if request.method in ('POST', 'DELETE', 'PUT', 'PATCH'):
            if request.user.is_authenticated:
                return request.user.role == 'admin'
        elif request.method in ('GET'):
            return True


class IsAuthorOrModeratorOrAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
                (request.user == obj.author) or (
                 request.user.role in ('admin', 'moderator'))
        )
