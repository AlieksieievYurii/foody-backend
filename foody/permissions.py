from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from users.models import User, UserRole


class IsAuthenticatedAndConfirmed(permissions.IsAuthenticated):
    def has_permission(self, request, view) -> bool:
        return super().has_permission(request, view) and request.user.is_email_confirmed


class IsExecutor(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        user_role = UserRole.objects.filter(user=request.user, is_confirmed=True).first()
        return user_role.role in (UserRole.UserRoleChoice.executor.name, UserRole.UserRoleChoice.administrator.name)


class IsAdministrator(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        else:
            return self.is_administrator(request.user)

    @staticmethod
    def is_administrator(user: User) -> bool:
        return UserRole.objects.filter(user=user,
                                       role=UserRole.UserRoleChoice.administrator.name,
                                       is_confirmed=True).exists()


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.pk == view.kwargs['pk']
