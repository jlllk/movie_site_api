from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from titles.validators import validate_year

User = get_user_model()


class Category(models.Model):
    """
    Модель описывает категории (типы) произведений.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Модель описывает жанры произведений.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Модель описывает произведения.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    year = models.IntegerField(null=True, blank=True, verbose_name='Год',
                               validators=[validate_year]
                               )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель описывает отзывы на произведения, которые оставляют пользователи.
    """
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(10, message='Значение должно быть от 1 до 10.'),
            MinValueValidator(1, message='Значение должно быть от 1 до 10.')
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('author', 'title')

    def __str__(self):
        return f'Автор: {self.author}. Отзыв: {self.text[:20]}...'


class Comment(models.Model):
    """
    Модель описывает комментарии к отзывам, которые оставляют пользователи.
    """
    text = models.TextField(verbose_name='Комментарий', )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Автор: {self.author}. Комментарий: {self.text[:20]}...'
