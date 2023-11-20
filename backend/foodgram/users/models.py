from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        'E-mail пользователя',
        max_length=254,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False
    )

    subscribers = models.ManyToManyField('self',
                                         symmetrical=False,
                                         through='Subscription')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',
                       'first_name',
                       'last_name',
                       'password']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='subscriber',
                             verbose_name='Подписчик')
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='subscribing',
                               verbose_name='Автор рецепта')
    subscribed_at = models.DateTimeField('Дата подписки',
                                         auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-subscribed_at',)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
