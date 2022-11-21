from django.contrib.auth import get_user_model
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingList, Tag)

User = get_user_model()


class UserFollowSerializer(serializers.ModelSerializer):

    following = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
    )
    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Такая подписка уже существует'
            )
        ]

    def validate(self, data):
        if (data['user'] == data['following']
                and self.context['request'].method == 'POST'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return FollowListSerializer(
            instance.following,
            context={'request': request}
        ).data


class FollowListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, user):
        current_user = self.context.get('current_user')
        other_user = user.following.all()
        if user.is_anonymous:
            return False
        if other_user.count() == 0:
            return False
        if Follow.objects.filter(user=user, following=current_user).exists():
            return True
        return False

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        request = self.context.get('request')
        return RecipeImageSerializer(
            recipes, many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CurrentUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'is_subscribed',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {"password": {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(following=obj, user=user).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')
        lookup_field = 'id'
        extra_kwargs = {'url': {'lookup_field': 'id'}}


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            read_only=True)
    name = serializers.SlugRelatedField(slug_field='name',
                                        source='ingredient',
                                        read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        slug_field='measurement_unit',
        source='ingredient', read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = '__all__'


class AddToIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('amount', 'id')


class RecipeSerializer(serializers.ModelSerializer):
    author = CurrentUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        recipe = obj
        queryset = recipe.recipes_ingredients_list.all()
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingList.objects.filter(recipe=obj, user=user).exists()


class RecipeImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.image.url
        return request.build_absolute_uri(image_url)


class RecipeFullSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    author = CurrentUserSerializer(read_only=True)
    ingredients = AddToIngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'author', 'ingredients',
            'name', 'text', 'cooking_time'
        )

    def create_bulk(self, recipe, ingredients_data):
        IngredientAmount.objects.bulk_create([IngredientAmount(
            ingredient=ingredient['ingredient'],
            recipe=recipe,
            amount=ingredient['amount']
        ) for ingredient in ingredients_data])

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        self.create_bulk(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_bulk(instance, ingredients_data)
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        instance.cooking_time = validated_data.pop('cooking_time')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.save()
        instance.tags.set(tags_data)
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError({
                    'ingredients': ('Число игредиентов должно быть больше 0')
                })
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0'
            )
        return data

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        requset = self.context.get('request')
        return RecipeImageSerializer(
            instance.recipe,
            context={'request': requset}
        ).data


class ShoppingListSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingList
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        requset = self.context.get('request')
        return RecipeImageSerializer(
            instance.recipe,
            context={'request': requset}
        ).data
