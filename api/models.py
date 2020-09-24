from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings

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
    role = models.CharField(max_length=20, choices=ROLES, default="user")
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


class Category(models.Model):

    name = models.CharField(max_length=40, verbose_name="Категория")
    slug = models.SlugField(max_length=50, verbose_name="slug", unique=True)

    class Meta:
        ordering = ["-slug"]

    def __str__(self):
        return self.name


class Title(models.Model):

    name = models.CharField(max_length=140,
                            verbose_name="Название фильма")
    year = models.IntegerField(
        validators=[MinValueValidator(1984), MaxValueValidator(2030)],
        verbose_name="Год выпуска"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="category_title",
        verbose_name="Категория"
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    title = models.ManyToManyField(Title,
                                   default=None,
                                   related_name='genres',
                                   blank=True,
                                   )

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name="reviews")
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name="reviews")
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)


class Comment(models.Model):
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name="comments")
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)
