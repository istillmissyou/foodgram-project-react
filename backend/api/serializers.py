from string import hexdigits

from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError)

from foodgram.settings import (INGREDIENTS_MIN_AMOUNT,
                               INGREDIENTS_MIN_AMOUNT_ERROR)
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag

User = get_user_model()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        lookup_field = 'id'
        extra_kwargs = {'url': {'lookup_field': 'id'}}

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


class AmountIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )
    name = SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )
    measurement_unit = SlugRelatedField(
        source='ingredient',
        slug_field='measuement_unit',
        read_only=True,
    )

    class Meta:
        model = AmountIngredient
        fields = '__all__'


class AddAmountIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )
    amount = IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('amount', 'id')


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


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


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
        read_only_fields = '__all__',

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

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
        ingredients_id = []
        for ingredient in data['ingredients']:
            if ingredient['amount'] < INGREDIENTS_MIN_AMOUNT:
                raise ValidationError(
                    INGREDIENTS_MIN_AMOUNT_ERROR.format(
                        min_amount=INGREDIENTS_MIN_AMOUNT,
                    )
                )
            ingredients_id.append(ingredient['id'])
        if len(ingredients_id) > len(set(ingredients_id)):
            raise ValidationError('Ингредиенты не должны повторяться')
        return data

    def get_ingredients(self, obj):
        return AmountIngredientSerializer(
            obj.ingredient.all(),
            many=True
        ).data

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


class RecipeFullSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = AddAmountIngredientSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )

    def create_bulk(self, recipe, ingredients_data):
        AmountIngredient.objects.bulk_create([AmountIngredient(
            recipe=recipe,
            ingredients=ingredient['ingredient'],
            amount=ingredient['amount']
        ) for ingredient in ingredients_data])

    @atomic
    def create(self, validated_data):
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.save()
        recipe.tags.set(validated_data.pop('tags'))
        self.create_bulk(
            recipe,
            validated_data.pop('ingredients')
        )
        return recipe

    @atomic
    def update(self, instance, validated_data):
        AmountIngredient.objects.filter(recipe=instance).delete()
        self.create_bulk(instance, validated_data.pop('ingredients'))
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        instance.cooking_time = validated_data.pop('cooking_time')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.save()
        instance.tags.set(validated_data.pop('tags'))
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
