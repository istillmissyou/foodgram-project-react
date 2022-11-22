from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, CharField, EmailField, ForeignKey,
                              Model, UniqueConstraint)

from foodgram.settings import MAX_LEN_USERS_CHARFIELD


class User(AbstractUser):
    email = EmailField(max_length=254, unique=True)
    username = CharField(max_length=MAX_LEN_USERS_CHARFIELD, unique=True)
    first_name = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    last_name = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    password = CharField(max_length=MAX_LEN_USERS_CHARFIELD)

    class Meta:
        ordering = ['username']
        constraints = (
            UniqueConstraint(
                fields=('email', 'username'),
                name='unique_username'
            ),
        )

    def __str__(self):
        return f'{self.username}: {self.email}'


class Subscription(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
