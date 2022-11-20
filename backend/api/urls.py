from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, FavoriteApiView, IngredientViewSet,
                    RecipeViewSet, TagViewSet)

router = DefaultRouter()
router.register(r'tags', TagViewSet, 'tags')
router.register(r'ingredients', IngredientViewSet, 'ingredients')
router.register(r'recipes', RecipeViewSet, 'recipes')
router.register('users', CustomUserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:favorite_id>/favorite/', FavoriteApiView.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
