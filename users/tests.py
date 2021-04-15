from unittest.mock import patch
from rest_framework import status
from django.test import TestCase

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from users.models import User, UserRole, RegistrationToken


class RegistrationTestCase(TestCase):
    USER_EMAIL: str = 'test@email.com'

    def setUp(self) -> None:
        self.client = APIClient()

    def _create_user(self, role: UserRole.UserRoleChoice):
        data = {'user': {'email': self.USER_EMAIL,
                         'first_name': 'Test first name',
                         'last_name': 'Test last name',
                         'phone_number': '+48 123',
                         'password': '123456789'},
                'role': role.name
                }
        return self.client.post('/users/register', data)

    @patch('users.serializers.email_manager_instance')
    def test_register_one_client(self, email_manager_instance):
        response = self._create_user(UserRole.UserRoleChoice.client)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserRole.objects.all().count(), 1)
        created_user = User.objects.get(email='test@email.com')
        self.assertFalse(created_user.is_email_confirmed)
        user_role = UserRole.objects.get(user=created_user)
        self.assertEqual(RegistrationToken.objects.all().count(), 1)
        self.assertTrue(user_role.is_confirmed)
        self.assertEqual(user_role.role, UserRole.UserRoleChoice.client.name)
        email_manager_instance.send_email_confirmation_to_client.assert_called_once()

    @patch('users.serializers.email_manager_instance')
    def test_register_one_executor(self, email_manager_instance):
        response = self._create_user(UserRole.UserRoleChoice.executor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserRole.objects.all().count(), 1)
        created_user = User.objects.get(email='test@email.com')
        self.assertFalse(created_user.is_email_confirmed)
        user_role = UserRole.objects.get(user=created_user)
        self.assertEqual(RegistrationToken.objects.all().count(), 1)
        self.assertFalse(user_role.is_confirmed)
        self.assertEqual(user_role.role, UserRole.UserRoleChoice.executor.name)
        email_manager_instance.send_executor_request_to_administrators.assert_called_once()
        email_manager_instance.send_email_confirmation_to_client.assert_called_once()

    @patch('users.serializers.email_manager_instance')
    def test_client_confirm_email(self, _):
        self._create_user(UserRole.UserRoleChoice.client)
        token = RegistrationToken.objects.first().token
        confirmation_endpoint = f'/users/confirm/{self.USER_EMAIL}/{token}'
        response = self.client.get(confirmation_endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RegistrationToken.objects.all().count(), 0)
        self.assertTrue(UserRole.objects.first().is_confirmed)
        self.assertTrue(User.objects.first().is_email_confirmed)

    @patch('users.serializers.email_manager_instance')
    def test_executor_confirm_email(self, _):
        self._create_user(UserRole.UserRoleChoice.executor)
        token = RegistrationToken.objects.first().token
        confirmation_endpoint = f'/users/confirm/{self.USER_EMAIL}/{token}'
        response = self.client.get(confirmation_endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RegistrationToken.objects.all().count(), 0)
        self.assertFalse(UserRole.objects.first().is_confirmed)
        self.assertTrue(User.objects.first().is_email_confirmed)

    def test_permission_denied_register_administrator(self):
        response = self._create_user(UserRole.UserRoleChoice.administrator)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserListTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @staticmethod
    def _create_user_model(email: str = 'default@email.com', password: str = '1234',
                           is_email_confirmed: bool = False) -> User:
        return User.objects.create_user(email=email,
                                        password=password,
                                        first_name='Test first name',
                                        last_name='Test last name',
                                        phone_number='+48 123',
                                        is_email_confirmed=is_email_confirmed)

    def _login(self, user: User, user_password: str):
        response = self.client.post('/api-token-auth/', {'username': user.email, 'password': user_password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["token"]}')

    def _create_mock_users(self):
        self._create_user_model(email='one@test.com')
        self._create_user_model(email='two@test.com')
        self._create_user_model(email='three@test.com')

    def test_get_list_is_not_authenticated(self):
        self._create_mock_users()
        resp = self.client.get('/users/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_list_of_users(self):
        self._create_mock_users()
        auth_user = self._create_user_model(is_email_confirmed=True)
        self._login(auth_user, user_password='1234')
        resp = self.client.get('/users/')

        self.assertEqual(resp.data['count'], User.objects.all().count())
        self.assertEqual(len(resp.data['results']), User.objects.all().count())

    def test_get_users_email_is_not_confirmed(self):
        self._create_mock_users()
        auth_user = self._create_user_model(is_email_confirmed=False)
        self._login(auth_user, user_password='1234')
        resp = self.client.get('/users/')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
