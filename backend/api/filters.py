from urllib.parse import unquote

from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)

from foodgram.settings import FALSE_SEARCH, TRUE_SEARCH
from recipes.models import Ingredient


class IngredientSearchFilter(FilterSet):
    name = CharFilter(method='search_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if value:
            if value[0] == '%':
                value = unquote(value)
            else:
                value = value.translate(
                    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./',
                    'йцукенгшщзхъфывапролджэячсмитьбю.'
                )
            value = value.lower()
            stw_queryset = list(queryset.filter(name__startswith=value))
            cnt_queryset = queryset.filter(name__contains=value)
            stw_queryset.extend(
                [i for i in cnt_queryset if i not in stw_queryset]
            )
            queryset = stw_queryset
        return queryset


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        method='get_tags',
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
