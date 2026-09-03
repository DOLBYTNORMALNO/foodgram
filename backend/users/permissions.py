from rest_framework import permissions


class RetrieveOrAuthenticated(permissions.BasePermission):
    """
    Профиль пользователя (GET /users/{id}/) доступен всем,
    изменение и /users/me/ — только авторизованным.
    """

    def has_permission(self, request, view):
        if view.action == 'retrieve':
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return True
        return bool(
            request.user.is_authenticated
            and (obj == request.user or request.user.is_admin)
        )
