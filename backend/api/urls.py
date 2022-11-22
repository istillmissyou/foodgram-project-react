from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientsViewSet, RecipesViewSet, TagsViewSet

router = DefaultRouter()
router.register('tags', TagsViewSet, 'tags')
router.register('ingredients', IngredientsViewSet, 'ingredients')
router.register('recipes', RecipesViewSet, 'recipes')

urlpatterns = [
    path('', include(router.urls)),
]
