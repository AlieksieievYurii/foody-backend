from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, APIException

from users import views
from users.mail import email_manager_instance
from users.models import User, UserRole, RegistrationToken


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data) -> User:
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name', 'phone_number', 'password', 'is_email_confirmed')
        extra_kwargs = {'password': {'write_only': True}}


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ('user', 'is_confirmed', 'role')
        extra_kwargs = {'is_confirmed': {'read_only': True}}


class UserRoleRegistrationFormSerializer(serializers.Serializer):
    user = UserSerializer()
    role = serializers.ChoiceField(UserRole.UserRoleChoice.choices)

    def update(self, instance, validated_data):
        raise APIException("Update is not implemented")

    def create(self, validated_data):
        user = self.fields['user'].create(validated_data.pop("user"))
        return self._create_role_and_send_confirmation(user, role=validated_data.pop("role"))

    def _create_role_and_send_confirmation(self, user: User, role: str) -> UserRole:
        if role == UserRole.UserRoleChoice.client.name:
            self._create_token_and_send_client_email_confirmation(user)
            return UserRole.objects.create(user=user, role=role, is_confirmed=True)
        elif role == UserRole.UserRoleChoice.executor.name:
            self._create_token_and_send_client_email_confirmation(user)
            email_manager_instance.send_executor_request_to_administrators(user)
            return UserRole.objects.create(user=user, role=role, is_confirmed=False)
        elif role == UserRole.UserRoleChoice.administrator.name:
            raise PermissionDenied("You cannot request administrator role yet")

    def _create_token_and_send_client_email_confirmation(self, user: User):
        token = RegistrationToken.create_token(user)
        confirmation_endpoint = self.context['request'].build_absolute_uri(reverse(views.confirm_user, kwargs={
            'email': user.email, 'token': token
        }))
        email_manager_instance.send_email_confirmation_to_client(confirmation_endpoint, user)
