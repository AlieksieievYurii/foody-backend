from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, generics, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView

from permissions import IsAuthenticatedAndConfirmed, IsAdministrator, IsOwner
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
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']
    lookup_field = 'user'

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserRoleView(RetrieveUpdateAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdministrator]


class UserListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]
