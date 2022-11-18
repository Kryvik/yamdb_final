from django.urls import reverse
from rest_framework import permissions
from users.models import ADMIN, MODERATOR


class IsAdminRoleOrGetListOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and (
                    request.user.role == ADMIN
                    or request.user.is_superuser)))

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and (
            request.user.role == ADMIN
            or request.user.is_superuser))


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and (
                    request.user.role == ADMIN
                    or request.user.is_superuser)))


class OnlyAdminOrMe(permissions.BasePermission):

    def has_permission(self, request, view):
        return ((request.user.is_authenticated
                 and reverse('users-me') == request.path)
                or (request.user.is_authenticated and (
                    request.user.role == ADMIN
                    or request.user.is_superuser)))


class IsAuthOrReadOnly(permissions.BasePermission):
    METHODS = ['PATCH', 'DELETE']
    ROLES = [ADMIN, MODERATOR]

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method in ['PATCH', 'DELETE']:
            if (request.user.role in self.ROLES
                    or request.user.is_superuser
                    or obj.author == request.user):
                return True
        return False
