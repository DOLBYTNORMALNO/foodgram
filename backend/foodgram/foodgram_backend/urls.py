from django.urls import path, include
from rest_framework.routers import DefaultRouter
from food.views import RecipeViewSet, TagViewSet, IngredientViewSet, UserViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
