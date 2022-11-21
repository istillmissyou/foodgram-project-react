from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCart, FavoriteApiView, FollowApiView,
                    FollowListApiView, IngredientViewSet, RecipeViewSet,
                    ShoppingView, TagViewSet, UserViewSet)

router = DefaultRouter()
router.register(r'tags', TagViewSet, 'tags')
router.register(r'ingredients', IngredientViewSet, 'ingredients')
router.register(r'recipes', RecipeViewSet, 'recipes')
router.register('users', UserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),
    path('recipes/<int:favorite_id>/favorite/', FavoriteApiView.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingView.as_view()),
    path('users/subscriptions/', FollowListApiView.as_view()),
    path('users/<int:following_id>/subscribe/', FollowApiView.as_view()),
]
