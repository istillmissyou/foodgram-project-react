from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (CustomUser, Favorite, Follow, Ingredient,
                     IngredientAmount, Recipe, ShoppingList, Tag)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'first_name', 'last_name',
                    'email', 'password', 'is_staff', 'is_active',)
    ordering = ('email',)
    search_fields = ('username', 'email',)
    ordering = ('email',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientsInline(admin.TabularInline):
    model = Ingredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'is_favorited',
        'ingredients',
    )
    search_fields = ('author', 'name')
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    def is_favorited(self, obj):
        return obj.favorites.count()

    def ingredients(self, obj):
        return list(obj.ingredients.all())
    ingredients.short_description = 'Ингредиенты'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount)
admin.site.register(ShoppingList)
admin.site.register(Tag)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follow)
