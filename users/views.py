from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, generics, permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView

from foody.permissions import IsAuthenticatedAndConfirmed, IsAdministrator, IsOwner
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


@api_view(['POST'])
@permission_classes([IsAuthenticatedAndConfirmed])
def become_cook(request):
    user_role = UserRole.objects.get(user=request.user)
    if user_role.role == UserRole.UserRoleChoice.executor:
        return Response('You are already a Cook', status=status.HTTP_400_BAD_REQUEST)
    user_role.role = UserRole.UserRoleChoice.executor
    user_role.is_confirmed = False
    user_role.save()

    return Response(status=status.HTTP_201_CREATED)


class RegisterUserView(CreateAPIView):
    serializer_class = UserRoleRegistrationFormSerializer
    permission_classes = (permissions.AllowAny,)


class UserRolesView(mixins.CreateModelMixin, mixins.ListModelMixin, generics.GenericAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'is_confirmed']
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

    def get_queryset(self):
        users_ids = self.request.query_params.get('users_ids', None)
        if users_ids:
            users = users_ids.split(',')
            return super().get_queryset().filter(id__in=users)
        else:
            return super().get_queryset()

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name='users_ids', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    ])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]
