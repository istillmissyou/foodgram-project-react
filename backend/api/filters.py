from django_filters.rest_framework import (BooleanFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)
from rest_framework.filters import SearchFilter

from foodgram.settings import FALSE_SEARCH, TRUE_SEARCH
from recipes.models import Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart',
    )
    is_favorited = BooleanFilter(
        method='get_is_favorited',
    )

    def get_tags(self, queryset, name, value):
        if value:
            return queryset.filter(
                tags__slug__in=self.request.query_params.get('tags'),
            ).distinct()
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        is_in_shopping = self.request.query_params.get('is_in_shopping_cart'),
        if (user := self.request.user).is_anonymous:
            return queryset
        if value:
            if is_in_shopping in TRUE_SEARCH:
                queryset = queryset.filter(cart=user.id)
            if is_in_shopping in FALSE_SEARCH:
                queryset = queryset.exclude(cart=user.id)
            return queryset
        return queryset

    def get_is_favorited(self, queryset, name, value):
        is_favorited = self.request.query_params.get('is_favorited')
        if (user := self.request.user).is_anonymous:
            return queryset
        if value:
            if is_favorited in TRUE_SEARCH:
                queryset = queryset.filter(favorite=user.id)
            if is_favorited in FALSE_SEARCH:
                queryset = queryset.exclude(favorite=user.id)
            return queryset
        return queryset
