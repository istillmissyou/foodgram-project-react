from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)
from foodgram.settings import MAX_LEN_RECIPES_CHARFIELD

User = get_user_model()


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
    is_favorited = ManyToManyField(
        User,
        related_name='favorites',
    )
    is_in_shopping_cart = ManyToManyField(
        User,
        related_name='carts',
    )
    image = ImageField(upload_to='recipes')
    name = CharField(max_length=MAX_LEN_RECIPES_CHARFIELD)
    text = TextField()
    cooking_time = PositiveSmallIntegerField(
        default=0,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(600),
        ),
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = UniqueConstraint(
            fields=('name', 'author'),
            name='unique_for_author'
        )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'


class AmountIngredient(Model):
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='ingredient',
    )
    ingredient = ForeignKey(
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
        constraints = [
            UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredient',
                ],
                name='amount_ingredient',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredient}'
