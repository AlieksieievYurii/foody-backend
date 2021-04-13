import random
import string

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from users.manages import UserManager
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email', unique=True)
    first_name = models.CharField('first_name', max_length=30, blank=False)
    last_name = models.CharField('last_name', max_length=30, blank=False)
    phone_number = models.CharField('phone_number', max_length=10, blank=False)
    date_joined = models.DateTimeField('date_joined', auto_now_add=True)
    is_staff = models.BooleanField('staff status', default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class UserRole(models.Model):
    class UserRoleChoice(models.TextChoices):
        client: tuple = ('client', 'client')
        executor: tuple = ('executor', 'executor')
        administrator: tuple = ('administrator', 'administrator')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField('is_confirmed', default=False)
    role = models.CharField('role', choices=UserRoleChoice.choices, max_length=15, blank=False)

    def __str__(self):
        return f'{self.user.email}: {self.role}'

    class Meta:
        unique_together = ['user', 'role']


class RegistrationToken(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    token = models.CharField('token', max_length=50, blank=False)

    @classmethod
    def create_token(cls, user_role: UserRole) -> str:
        """
        Creates a registration token for a given User

        :param user_role: UserType for who need to generate token
        :return: token
        """

        def _token_generator(size=50, chars=string.ascii_lowercase + string.digits) -> str:
            return ''.join(random.choice(chars) for _ in range(size))

        token = _token_generator()
        cls.objects.update_or_create(user_role=user_role, token=token)
        return token
