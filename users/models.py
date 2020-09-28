from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
        ('Django admin', 'Django admin')
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50,
                                blank=True,
                                null=True,
                                default='None',
                                )
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    bio = models.TextField(blank=True,
                                   null=True,
                                   )
    first_name = models.CharField(max_length=40,
                                  blank=True,
                                  null=True,
                                  )
    last_name = models.CharField(max_length=40,
                                 blank=True,
                                 null=True,
                                 )
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self