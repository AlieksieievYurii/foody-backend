from rest_framework import serializers
from rest_framework.exceptions import APIException

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data) -> User:
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        self._create_confirmation(user.type)
        return user

    def _create_confirmation(self, user_type: str) -> None:
        if user_type == User.UserType.client.name:
            self._send_email_confirmation_to_client()
        elif user_type in (User.UserType.executor.name, User.UserType.administrator.name):
            self._send_email_confirmation_to_administrators()
        else:
            raise APIException("Unsupported User's type yet")

    def _send_email_confirmation_to_client(self) -> None:
        # TODO() Implement sending user confirmation
        pass

    def _send_email_confirmation_to_administrators(self) -> None:
        # TODO() Implement sending user confirmation
        pass

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'is_confirmed', 'password', 'type')
        extra_kwargs = {'password': {'write_only': True}}
