from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, ManyToManyField
from foodgram.settings import MAX_LEN_USERS_CHARFIELD


class User(AbstractUser):
    email = EmailField(max_length=254, unique=True)
    username = CharField(max_length=MAX_LEN_USERS_CHARFIELD, unique=True)
    first_name = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    last_name = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    password = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    is_subscribed = ManyToManyField(
        to='self',
        symmetrical=False,
        related_name='subscribes',
    )

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f'{self.username}: {self.email}'
