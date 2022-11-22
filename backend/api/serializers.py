from string import hexdigits

from django.contrib.auth import get_user_model
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError)

from foodgram.settings import (INGREDIENTS_MIN_AMOUNT,
                               INGREDIENTS_MIN_AMOUNT_ERROR)
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag

User = get_user_model()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',

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
        read_only_fields = '__all__',


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

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
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscribe.filter(id=obj.id).exists()

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


class RecipeViewSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = SerializerMethodField(
        read_only=True,
        source='get_ingredients'
    )
    is_favorited = SerializerMethodField(
        read_only=True,
        source='get_is_favorited'
    )
    is_in_shopping_cart = SerializerMethodField(
        read_only=True,
        source='get_is_in_shopping_cart'
    )

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
            'cooking_time'
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('recipe__amount'),
        )


class UserSubscribeSerializer(UserSerializer):
    recipes = RecipeViewSerializer(many=True, read_only=True)
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
        read_only_fields = '__all__',

    def get_recipes_count(self, obj):
        return obj.recipes.count()

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


class RecipeCreateSerializer(ModelSerializer):
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

    def validate(self, data):
        for ingredient in self.initial_data.get('ingredients'):
            if int(ingredient['amount']) < INGREDIENTS_MIN_AMOUNT:
                raise ValidationError(
                    INGREDIENTS_MIN_AMOUNT_ERROR.format(
                        min_amount=INGREDIENTS_MIN_AMOUNT,
                    )
                )
        return data

    def create_bulk_ingredients(self, recipe, ingredients_data):
        AmountIngredient.objects.bulk_create([AmountIngredient(
            ingredient=ingredient['id'],
            recipe=recipe,
            amount=ingredient['amount']
        ) for ingredient in ingredients_data])

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            image=validated_data.pop('image'),
            **validated_data,
        )
        recipe.save()
        recipe.tags.set(validated_data.pop('tags'))
        self.create_bulk_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        AmountIngredient.objects.filter(recipe=recipe).delete()
        self.create_bulk_ingredients(recipe, ingredients_data)
        recipe.name = validated_data.pop('name')
        recipe.text = validated_data.pop('text')
        recipe.cooking_time = validated_data.pop('cooking_time')
        if validated_data.get('image') is not None:
            recipe.image = validated_data.pop('image')
        recipe.save()
        recipe.tags.set(tags_data)
        return recipe

    def to_representation(self, instance):
        return RecipeViewSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
