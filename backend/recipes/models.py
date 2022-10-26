from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (CASCADE, CharField, ForeignKey, ImageField,
                              ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)

from foodgram.settings import MAX_LEN_RECIPES_CHARFIELD

User = get_user_model()


class Tag(Model):
    name = CharField(max_length=MAX_LEN_RECIPES_CHARFIELD, unique=True)
    color = CharField(
        verbose_name='Цветовой HEX-код',
        max_length=6,
        blank=True,
        null=True,
        default='FF',
    )
    slug = SlugField(unique=True)

    class Meta:
        ordering = ['name']


class Ingredient(Model):
    name = CharField(max_length=MAX_LEN_RECIPES_CHARFIELD)
    measurement_unit = CharField(max_length=MAX_LEN_RECIPES_CHARFIELD)

    class Meta:
        ordering = ['name']


class Recipe(Model):
    tags = ManyToManyField(Tag, related_name='recipes')
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='recipes',
    )
    ingredients = ManyToManyField(
        Ingredient,
        through='recipes.AmountIngredient',
    )
    is_favorited = ManyToManyField(User, related_name='favorites')
    is_in_shopping_cart = ManyToManyField(User, related_name='carts')
    image = ImageField(upload_to='recipes')
    name = CharField(max_length=MAX_LEN_RECIPES_CHARFIELD)
    text = TextField()
    cooking_time = PositiveSmallIntegerField(
        default=0,
        validators=(MinValueValidator(1, 'Одно мгновенье!'),
                    MaxValueValidator(600, 'Очень долго...'),),
    )


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
            MinValueValidator(1, 'Хоть что-то'),
            MaxValueValidator(10000, 'Слишком много!'),
        ),
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['recipe', 'ingredient'],
                             name='amount_ingredient')
        ]
