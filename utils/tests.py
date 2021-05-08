from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, UserRole


class ApiTestCase(TestCase):
    DEFAULT_EMAIL: str = 'default@email.com'
    DEFAULT_PASSWORD: str = '1234'

    def setUp(self) -> None:
        self.client = APIClient()

    def _create_default_user_and_log_in(self, is_email_confirmed: bool = True,
                                        role: UserRole.UserRoleChoice = UserRole.UserRoleChoice.client,
                                        is_role_confirmed: bool = True) -> User:
        user = self._create_user_model(is_email_confirmed=is_email_confirmed)
        UserRole.objects.create(user=user, role=role.name, is_confirmed=is_role_confirmed)
        self._login(user)
        return user

    @staticmethod
    def _create_user_model(email: str = DEFAULT_EMAIL, password: str = DEFAULT_PASSWORD,
                           is_email_confirmed: bool = False) -> User:
        return User.objects.create_user(email=email,
                                        password=password,
                                        first_name='Test first name',
                                        last_name='Test last name',
                                        phone_number='+48 123',
                                        is_email_confirmed=is_email_confirmed)

    def _login(self, user: User, user_password: str = DEFAULT_PASSWORD):
        response = self.client.post('/api-token-auth/', {'username': user.email, 'password': user_password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["token"]}')

    def _register_user(self, email: str = DEFAULT_EMAIL, password: str = DEFAULT_PASSWORD,
                       role: UserRole.UserRoleChoice = UserRole.UserRoleChoice.client):
        data = {'user': {'email': email,
                         'first_name': 'Test first name',
                         'last_name': 'Test last name',
                         'phone_number': '+48 123',
                         'password': password},
                'role': role.name
                }
        self.client.credentials()
        return self.client.post('/users/register', data)
