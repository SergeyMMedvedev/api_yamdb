import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings


class Category(models.Model):

    name = models.CharField(max_length=40, verbose_name='Категория')
    slug = models.SlugField(max_length=50, verbose_name='slug', unique=True)

    class Meta:
        ordering = ['-slug']

    def __str__(self):
        return self.name


class Title(models.Model):

    name = models.CharField(
        max_length=140, verbose_name='Название фильма'
    )
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(datetime.date.today().year)],
        verbose_name='Год выпуска'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='category_title',
        verbose_name='Категория'
    )
    description = models.TextField(default='')
    rating = models.FloatField(default=None, blank=True, null=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    title = models.ManyToManyField(
        Title, default=None, related_name='genre', blank=True
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
