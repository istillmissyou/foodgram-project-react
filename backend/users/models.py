from django.contrib.auth.models import AbstractUser
from django.db.models import (CharField, CheckConstraint, EmailField,
                              ManyToManyField, Q)
from foodgram.settings import MAX_LEN_USERS_CHARFIELD, MIN_LEN_USERNAME


class User(AbstractUser):
    email = EmailField(max_length=254, unique=True)
    username = CharField(max_length=MAX_LEN_USERS_CHARFIELD, unique=True)
    first_name = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    last_name = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    password = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    is_subscribed = ManyToManyField(to='self', symmetrical=False)

    class Meta:
        ordering = ['username']
        constraints = (
            CheckConstraint(check=Q(username__length__gte=MIN_LEN_USERNAME))
        )

    def __str__(self):
        return f'{self.username}: {self.email}'
