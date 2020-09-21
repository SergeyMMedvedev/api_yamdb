from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Category(models.Model):

    name = models.CharField(
        "name", max_length=40, verbose_name="Категория"
    )
    slug = models.SlugField("slug", max_length=50, verbose_name="slug")

    class Meta:
        ordering = ["-slug"]


class Titles(models.Model):

    name = models.CharField(
        "movie", max_length=140, verbose_name="Название фильма"
    )
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


