from datetime import datetime
from urllib.parse import unquote

from django.db.models import F, Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from foodgram.settings import DATE_TIME_FORMAT
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag

from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrModerator
from .serializers import (IngredientSerializer, RecipeSerializer,
                          TagSerializer, UserSubscribeSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class CustomUserViewSet(UserViewSet, AddDelViewMixin):
    pagination_class = PageLimitPagination
    add_serializer = UserSubscribeSerializer

    @action(methods=('get', 'post'), detail=True)
    def subscribe(self, request, id):
        return self.add_del_obj(id, 'subscribe')

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        queryset = Ingredient.objects.all()
        if name:
            if name[0] == '%':
                name = unquote(name)
            else:
                name = name.translate(str.maketrans(
                    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./',
                    'йцукенгшщзхъфывапролджэячсмитьбю.'
                ))
            name = name.lower()
            stw_queryset = list(queryset.filter(name__startswith=name))
            cnt_queryset = queryset.filter(name__contains=name)
            stw_queryset.extend(
                [i for i in cnt_queryset if i not in stw_queryset]
            )
            return stw_queryset
        return queryset


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrModerator]

    def get_queryset(self):
        queryset = Recipe.objects.select_related('author')
        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        is_favorited = self.request.query_params.get('is_favorited')
        user = self.request.user
        true_search = ('1', 'true',)
        false_search = ('0', 'false',)
        if (tags := self.request.query_params.getlist('tags')):
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()
        if (author := self.request.query_params.get('author')):
            queryset = queryset.filter(author=author)

        if user.is_anonymous:
            return queryset
        if is_in_shopping in true_search:
            queryset = queryset.filter(cart=user.id)
        if is_in_shopping in false_search:
            queryset = queryset.exclude(cart=user.id)

        if is_favorited in true_search:
            queryset = queryset.filter(favorite=user.id)
        if is_favorited in false_search:
            queryset = queryset.exclude(favorite=user.id)
        return queryset

    @action(methods=('get', 'post', 'delete',), detail=True)
    def favorite(self, request, pk):
        return self.add_del_obj(pk, 'favorite')

    @action(methods=('get', 'post', 'delete',), detail=True)
    def shopping_cart(self, request, pk):
        return self.add_del_obj(pk, 'shopping_cart')

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        amount_ingredients = AmountIngredient.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для: {user.first_name}\n\n'
            f'{datetime.now().strftime(DATE_TIME_FORMAT)}\n\n'
        )
        for ing in amount_ingredients:
            shopping_list += (
                f'{ing["ingredient"]}: {ing["amount"]} {ing["measure"]}\n'
            )

        shopping_list += '\n\nПриятного аппетита!'

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
