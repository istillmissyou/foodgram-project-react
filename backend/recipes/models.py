from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (CASCADE, CharField, DateTimeField, EmailField,
                              ForeignKey, ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)
from foodgram.settings import (MAX_LEN_RECIPES_CHARFIELD,
                               MAX_LEN_USERS_CHARFIELD)


class User(AbstractUser):
    email = EmailField(max_length=254, unique=True)
    username = CharField(max_length=MAX_LEN_USERS_CHARFIELD, unique=True)
    first_name = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    last_name = CharField(max_length=MAX_LEN_USERS_CHARFIELD)
    password = CharField(max_length=MAX_LEN_USERS_CHARFIELD)

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f'{self.username}: {self.email}'


class Follow(Model):
    following = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following'
    )
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower'
    )

    class Meta:
        UniqueConstraint(fields=['following', 'user'], name='follow_unique')

    def __str__(self):
        return f"{self.user} follows {self.following}"


class Tag(Model):
    name = CharField(
        max_length=MAX_LEN_RECIPES_CHARFIELD,
        unique=True,
    )
    color = CharField(
        verbose_name='Цветовой HEX-код',
        max_length=6,
        unique=True,
        default='FF',
    )
    slug = SlugField(
        unique=True,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'


class Ingredient(Model):
    name = CharField(max_length=MAX_LEN_RECIPES_CHARFIELD)
    measurement_unit = CharField(max_length=MAX_LEN_RECIPES_CHARFIELD)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(Model):
    tags = ManyToManyField(
        Tag,
        related_name='recipes',
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='recipes',
    )
    ingredients = ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='recipes.AmountIngredient',
    )
    cart = ManyToManyField(
        User,
        related_name='carts',
    )
    image = ImageField(upload_to='recipes/')
    name = CharField(
        max_length=MAX_LEN_RECIPES_CHARFIELD,
    )
    text = TextField()
    cooking_time = PositiveSmallIntegerField(
        default=0,
        validators=(
            MinValueValidator(1),
        ),
    )
    pub_date = DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author'
            ),
        )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'


class Favorite(Model):
    user = ForeignKey(
        User,
        related_name='favorites',
        on_delete=CASCADE,
    )
    recipe = ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=CASCADE,
    )
    added = DateTimeField(auto_now_add=True)

    class Meta:
        UniqueConstraint(fields=['recipe', 'user'], name='favorite_unique')

    def __str__(self):
        return f"{self.user} has favorites: {self.recipe.name}"


class AmountIngredient(Model):
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='ingredient',
    )
    ingredients = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        related_name='recipe',
    )
    amount = PositiveSmallIntegerField(
        default=0,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10000),
        ),
    )

    class Meta:
        ordering = ['recipe']
        constraints = (
            UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredients',
                ],
                name='amount_ingredient',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'
