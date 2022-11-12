from string import hexdigits

from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag, User
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__'

    def validate_color(self, color):
        color = str(color).strip(' #')
        if len(color) not in (3, 6):
            raise ValidationError(f'{color} wrong length!')
        if not set(color).issubset(hexdigits):
            raise ValidationError(f'{color} is not hexadecimal!')
        return f'#{color}'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__'


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscribe.filter(id=obj.id).exists

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__'


class UserSubscribeSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__'

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.carts.filter(id=obj.id).exists()

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            AmountIngredient.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.image = validated_data.get(
            'image', recipe.image)
        recipe.name = validated_data.get(
            'name', recipe.name)
        recipe.text = validated_data.get(
            'text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                AmountIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredients=ingredient['ingredient'],
                    amount=ingredient['amount'],
                )
        recipe.save()
        return recipe
