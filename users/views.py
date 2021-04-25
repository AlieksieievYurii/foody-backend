from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, generics, permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView

from permissions import IsAuthenticatedAndConfirmed, IsAdministrator, IsOwner
from users.mail import email_manager_instance
from users.models import User, UserRole, RegistrationToken
from users.serializers import UserSerializer, UserRoleSerializer, UserRoleRegistrationFormSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class AuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def confirm_user(request, email: str, token: str):
    def _send_email_to_admins_if_executor_request(user: User):
        try:
            UserRole.objects.get(user=user, role=UserRole.UserRoleChoice.executor.name, is_confirmed=False)
        except UserRole.DoesNotExist:
            pass
        else:
            email_manager_instance.send_executor_request_to_administrators(user)

    try:
        registration_token = RegistrationToken.objects.get(token=token, user__email=email)
    except RegistrationToken.DoesNotExist:
        return render(request, 'users/email_confirmation.html', {'expired': True}, status=status.HTTP_404_NOT_FOUND)
    else:
        registration_token.user.is_email_confirmed = True
        registration_token.user.save()
        registration_token.delete()
        _send_email_to_admins_if_executor_request(user=registration_token.user)
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
