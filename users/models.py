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
    is_confirmed = models.BooleanField('is_confirmed', default=False)
    is_staff = models.BooleanField(
        'staff status',
        default=True,
        help_text='Designates whether the user can log into this admin site.',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
