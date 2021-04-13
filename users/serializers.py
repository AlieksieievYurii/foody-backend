from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, APIException

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
        fields = ('pk', 'email', 'first_name', 'last_name', 'phone_number', 'password')
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
        instance = UserRole.objects.create(user=user, role=validated_data.pop("role"))
        self._send_role_confirmation(instance)
        return instance

    def _send_role_confirmation(self, instance: UserRole):
        if instance.role == UserRole.UserRoleChoice.client.name:
            self._create_token_and_send_client_email_confirmation(instance)
        elif instance.role == UserRole.UserRoleChoice.executor.name:
            email_manager_instance.send_executor_request_to_administrators(instance)
        elif instance.role == UserRole.UserRoleChoice.administrator.name:
            raise PermissionDenied("You cannot request administrator role yet")

    def _create_token_and_send_client_email_confirmation(self, instance: UserRole):
        token = RegistrationToken.create_token(instance)
        email_manager_instance.send_email_confirmation_to_client(self.context['request'], instance.user, token)
