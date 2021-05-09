from unittest.mock import patch
from rest_framework import status

from users.models import User, UserRole, RegistrationToken
from utils.tests import ApiTestCase


class RegistrationTestCase(ApiTestCase):

    @patch('users.serializers.email_manager_instance')
    def test_register_one_client(self, email_manager_instance):
        response = self._register_user()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserRole.objects.all().count(), 1)
        created_user = User.objects.get(email=self.DEFAULT_EMAIL)
        self.assertFalse(created_user.is_email_confirmed)
        user_role = UserRole.objects.get(user=created_user)
        self.assertEqual(RegistrationToken.objects.all().count(), 1)
        self.assertTrue(user_role.is_confirmed)
        self.assertEqual(user_role.role, UserRole.UserRoleChoice.client.name)
        email_manager_instance.send_email_confirmation_to_client.assert_called_once()

    @patch('users.serializers.email_manager_instance')
    def test_register_one_executor(self, email_manager_instance):
        response = self._register_user(role=UserRole.UserRoleChoice.executor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserRole.objects.all().count(), 1)
        created_user = User.objects.get(email=self.DEFAULT_EMAIL)
        self.assertFalse(created_user.is_email_confirmed)
        user_role = UserRole.objects.get(user=created_user)
        self.assertEqual(RegistrationToken.objects.all().count(), 1)
        self.assertFalse(user_role.is_confirmed)
        self.assertEqual(user_role.role, UserRole.UserRoleChoice.executor.name)
        email_manager_instance.send_executor_request_to_administrators.assert_not_called()
        email_manager_instance.send_email_confirmation_to_client.assert_called_once()

    def test_wrong_confirmation_token(self):
        user = self._create_user_model()
        UserRole.objects.create(user=user, role=UserRole.UserRoleChoice.client.name)
        RegistrationToken.objects.create(user=user, token='123456')
        response = self.client.get(f'/users/confirm/{self.DEFAULT_EMAIL}/12221')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('users.views.email_manager_instance')
    def test_confirm_executor(self, email_manager_instance):
        user = self._create_user_model()
        UserRole.objects.create(user=user, role=UserRole.UserRoleChoice.executor.name)
        token = RegistrationToken.objects.create(user=user, token='123456')
        response = self.client.get(f'/users/confirm/{self.DEFAULT_EMAIL}/{token.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        email_manager_instance.send_executor_request_to_administrators.assert_called_once()

    @patch('users.serializers.email_manager_instance')
    def test_client_confirm_email(self, _):
        self._register_user()
        token = RegistrationToken.objects.first().token
        response = self.client.get(f'/users/confirm/{self.DEFAULT_EMAIL}/{token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RegistrationToken.objects.all().count(), 0)
        self.assertTrue(UserRole.objects.first().is_confirmed)
        self.assertTrue(User.objects.first().is_email_confirmed)

    @patch('users.serializers.email_manager_instance')
    def test_executor_confirm_email(self, _):
        self._register_user(role=UserRole.UserRoleChoice.executor)
        token = RegistrationToken.objects.first().token
        confirmation_endpoint = f'/users/confirm/{self.DEFAULT_EMAIL}/{token}'
        response = self.client.get(confirmation_endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RegistrationToken.objects.all().count(), 0)
        self.assertFalse(UserRole.objects.first().is_confirmed)
        self.assertTrue(User.objects.first().is_email_confirmed)

    def test_permission_denied_register_administrator(self):
        response = self._register_user(role=UserRole.UserRoleChoice.administrator)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserListTestCase(ApiTestCase):
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
        self._login(auth_user, user_password=self.DEFAULT_PASSWORD)
        resp = self.client.get('/users/')

        self.assertEqual(resp.data['count'], User.objects.all().count())
        self.assertEqual(len(resp.data['results']), User.objects.all().count())

    def test_get_users_email_is_not_confirmed(self):
        self._create_mock_users()
        auth_user = self._create_user_model(is_email_confirmed=False)
        self._login(auth_user, user_password=self.DEFAULT_PASSWORD)
        resp = self.client.get('/users/')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class UserRolesTestCase(ApiTestCase):
    def _create_mock_users(self):
        user_1 = self._create_user_model(email='one@test.com')
        user_2 = self._create_user_model(email='two@test.com')
        user_3 = self._create_user_model(email='three@test.com')
        UserRole.objects.create(user=user_1, is_confirmed=False, role=UserRole.UserRoleChoice.client)
        UserRole.objects.create(user=user_2, is_confirmed=True, role=UserRole.UserRoleChoice.client)
        UserRole.objects.create(user=user_3, is_confirmed=True, role=UserRole.UserRoleChoice.executor)

    def test_get_roles(self):
        self._create_default_user_and_log_in()
        response = self.client.get('/users/roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_roles_not_authenticated(self):
        self._create_mock_users()
        response = self.client.get('/users/roles/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_roles_is_authenticated_not_confirmed(self):
        self._create_default_user_and_log_in(is_email_confirmed=False)
        response = self.client.get('/users/roles/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrator_change_role(self):
        user = self._create_user_model(email='user@test.email', is_email_confirmed=True)
        user_model = UserRole.objects.create(user=user, role=UserRole.UserRoleChoice.client, is_confirmed=True)

        self._create_default_user_and_log_in(is_email_confirmed=True, role=UserRole.UserRoleChoice.administrator)

        response = self.client.patch(f'/users/role/{user.pk}', {'role': UserRole.UserRoleChoice.executor})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_model.refresh_from_db()
        self.assertEqual(user_model.role, UserRole.UserRoleChoice.executor)

    def test_client_cannot_change_roles(self):
        user = self._create_user_model(email='user@test.email', is_email_confirmed=True)
        UserRole.objects.create(user=user, role=UserRole.UserRoleChoice.client, is_confirmed=True)

        self._create_default_user_and_log_in(is_email_confirmed=True, role=UserRole.UserRoleChoice.client)

        response = self.client.patch(f'/users/role/{user.pk}', {'role': UserRole.UserRoleChoice.executor})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_executor_cannot_change_roles(self):
        user = self._create_user_model(email='user@test.email', is_email_confirmed=True)
        UserRole.objects.create(user=user, role=UserRole.UserRoleChoice.client, is_confirmed=True)

        self._create_default_user_and_log_in(is_email_confirmed=True, role=UserRole.UserRoleChoice.executor)

        response = self.client.patch(f'/users/role/{user.pk}', {'role': UserRole.UserRoleChoice.executor})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrator_create_role(self):
        user = self._create_user_model(email='user@test.email', is_email_confirmed=True)
        self._create_default_user_and_log_in(is_email_confirmed=True, role=UserRole.UserRoleChoice.administrator)
        response = self.client.post(f'/users/roles/', {
            'user': user.pk,
            'is_confirmed': True,
            'role': UserRole.UserRoleChoice.executor.name})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_update_personal_information(self):
        user = self._create_default_user_and_log_in(is_email_confirmed=True, role=UserRole.UserRoleChoice.client)
        response = self.client.patch(f'/users/{user.pk}', {'first_name': 'Yurii'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Yurii')

    def test_user_update_another_personal_information(self):
        self._create_default_user_and_log_in(is_email_confirmed=True, role=UserRole.UserRoleChoice.client)
        some_user = self._create_user_model(email='some.user@email.com')
        response = self.client.patch(f'/users/{some_user.pk}', {'first_name': 'Yurii'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
