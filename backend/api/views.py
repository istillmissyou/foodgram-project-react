from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.utils import timezone
from django_filters.rest_framework.backends import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .filters import RecipeFilter, IngredientSearchFilter
from foodgram.settings import DATE_TIME_FORMAT
from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrModerator
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer,
                          UserSubscribeSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


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
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [IngredientSearchFilter, ]
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    add_serializer = ShortRecipeSerializer
    permission_classes = [IsAuthorOrAdminOrModerator]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination

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
        ).annotate(count=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для: {user.first_name}\n\n'
            f'{timezone.now().strftime(DATE_TIME_FORMAT)}\n\n'
        )
        for ing in amount_ingredients:
            shopping_list += (
                f'{ing["ingredient"]}: {ing["count"]} {ing["measure"]}\n'
            )
        shopping_list += '\n\nПриятного аппетита!'
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
