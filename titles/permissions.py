from rest_framework.permissions import SAFE_METHODS, BasePermission
from users.models import UserRole


class ReadOnly(BasePermission):
    """
    Разрешен метод 'GET' для всех пользователей.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Доступ разрешен администратору.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin


class IsModerator(BasePermission):
    """
    Доступ разрешен модератору.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == UserRole.MODERATOR)

    def has_object_permission(self, request, view, obj):
        return request.user.role == UserRole.MODERATOR


class IsOwner(BasePermission):
    """
    Изменять объекты могут только их владельцы.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
