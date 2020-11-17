from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class CustomUser(AbstractUser):
    role = models.CharField(
        choices=UserRole.choices,
        default=UserRole.USER,
        max_length=50,
        verbose_name='Роль',
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Биография',
    )

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_personnel(self):
        return (self.role in (UserRole.ADMIN, UserRole.MODERATOR) or
                self.is_superuser)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
