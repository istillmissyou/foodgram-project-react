from django.contrib.admin import ModelAdmin, TabularInline, site

from .models import AmountIngredient, Ingredient, Recipe, Tag


class IngredientAdmin(ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientsInline(TabularInline):
    model = Ingredient


class RecipeAdmin(ModelAdmin):
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
    inlines = (IngredientsInline,)

    def is_favorited(self, obj):
        return obj.favorites.count()

    def ingredients(self, obj):
        return list(obj.ingredients.all())
    ingredients.short_description = 'Ингредиенты'


site.register(Recipe, RecipeAdmin)
site.register(Ingredient, IngredientAdmin)
site.register(AmountIngredient)
site.register(Tag)
