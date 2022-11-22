from django.contrib import admin

from .models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag, TagInRecipe)


class DisplayEmptyFieldMixin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class TagInRecipeInline(admin.TabularInline):
    model = TagInRecipe
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'cooking_time',
        'pub_date',
        'count_favorite'
    )
    search_fields = ('author__username', 'name',)
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('count_favorite',)
    inlines = (IngredientInRecipeInline, TagInRecipeInline)
    exclude = ('tags', 'ingredients')

    def count_favorite(self, obj):
        return obj.favorite_recipe.count()


@admin.register(Favorites)
class FavoritesAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)
