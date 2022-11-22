from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
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


class Tag(Model):
    name = CharField(
        max_length=MAX_LEN_RECIPES_CHARFIELD,
        unique=True,
    )
    color = CharField(
        verbose_name='Цветовой HEX-код',
        max_length=7,
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
    name = CharField(max_length=MAX_LEN_RECIPES_CHARFIELD, unique=True)
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
        through='recipes.IngredientInRecipe',
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


class IngredientInRecipe(Model):
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='ingredient_recipe'
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        related_name='ingredient_recipe'
    )
    amount = PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1),
        )
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount}'
                f' {self.ingredient.measurement_unit}')


class TagInRecipe(Model):
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='tag_recipe'
    )
    tag = ForeignKey(
        Tag,
        on_delete=CASCADE,
        related_name='tag_recipe'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'{self.tag.name} для рецепта {self.recipe.name}'


class Favorites(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='favorite_user',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='favorite_recipe'
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorites'
            ),
        )

    def __str__(self):
        return f'{self.recipe.name} - любимый рецепт {self.user}'


class ShoppingCart(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='shopping_cart_user',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='shopping_cart_recipe',
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_cart_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
