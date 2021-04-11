import random
import string

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from users.manages import UserManager
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        client: tuple = ('client', 'client')
        executor: tuple = ('executor', 'executor')
        administrator: tuple = ('administrator', 'administrator')

    email = models.EmailField('email', unique=True)
    first_name = models.CharField('first_name', max_length=30, blank=False)
    last_name = models.CharField('last_name', max_length=30, blank=False)
    phone_number = models.CharField('phone_number', max_length=10, blank=False)
    date_joined = models.DateTimeField('date_joined', auto_now_add=True)
    is_confirmed = models.BooleanField('is_confirmed', default=False)
    type = models.CharField('type', choices=UserType.choices, max_length=15, blank=False)
    is_staff = models.BooleanField('staff status', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class RegistrationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField('token', max_length=50, blank=False)

    @classmethod
    def create_token(cls, user: User) -> str:
        """
        Creates a registration token for a given User

        :param user: User for who need to generate token
        :return: token
        """

        def _token_generator(size=50, chars=string.ascii_lowercase + string.digits) -> str:
            return ''.join(random.choice(chars) for _ in range(size))

        token = _token_generator()
        cls.objects.update_or_create(user=user, token=token)
        return token
