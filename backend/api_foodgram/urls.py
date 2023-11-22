from django.urls import include, path
from rest_framework import routers

from .views import IngredientView, RecipeViewSet, TagView

router = routers.DefaultRouter()
router.register(r'tags', TagView)
router.register(r'ingredients', IngredientView)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
