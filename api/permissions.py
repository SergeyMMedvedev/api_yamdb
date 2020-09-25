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


class OnlyOneReview(BasePermission):
    def has_permission(self, request, view):
        title_id = int(request.path.split('/')[4])
        if request.method in ('POST'):
            reviews_title_ids = []
            for review in request.user.reviews.all():
                reviews_title_ids.append(review.title.id)
            return title_id not in reviews_title_ids
        else:
            return True


class IsAuthorOrReadOnlyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('DELETE', 'PUT', 'PATCH'):
            return request.user == obj.author
        return True


class IsAuthorOrModeratorOrAdminOrReadOnlyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('DELETE', 'PUT', 'PATCH'):
            return (request.user == obj.author) or (request.user.role == 'admin') or (request.user.role == 'moderator')
        return True