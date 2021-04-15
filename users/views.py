from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, generics, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import SAFE_METHODS

from users.models import User, UserRole, RegistrationToken
from users.serializers import UserSerializer, UserRoleSerializer, UserRoleRegistrationFormSerializer


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def confirm_user(request, email: str, token: str):
    try:
        registration_token = RegistrationToken.objects.get(token=token, user__email=email)
    except ObjectDoesNotExist:
        return render(request, 'users/email_confirmation.html', {'expired': True})
    else:
        registration_token.user.is_email_confirmed = True
        registration_token.user.save()
        registration_token.delete()
        return render(request, 'users/email_confirmation.html')


class RegisterUserView(CreateAPIView):
    serializer_class = UserRoleRegistrationFormSerializer
    permission_classes = (permissions.AllowAny,)


class UserRolesView(mixins.CreateModelMixin, mixins.ListModelMixin, generics.GenericAPIView):
    class AdministratorCanUpdate(permissions.BasePermission):
        def has_permission(self, request, view):
            if request.method in SAFE_METHODS:
                return True
            elif request.method == 'UPDATE':
                return self.is_administrator(request.user)
            else:
                return False

        @staticmethod
        def is_administrator(user: User) -> bool:
            return UserRole.objects.filter(user=user, role=UserRole.UserRoleChoice.administrator.name).exists()

    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [AdministratorCanUpdate]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']
    lookup_field = 'user'

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserRoleView(RetrieveUpdateAPIView):
    class OnlyAdministratorCanUpdate(permissions.BasePermission):
        def has_permission(self, request, view) -> bool:
            if request.method == 'GET':
                return True
            else:
                return UserRole.objects.filter(user=request.user,
                                               role=UserRole.UserRoleChoice.administrator.name).exists()

    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [OnlyAdministratorCanUpdate]


class UserListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
