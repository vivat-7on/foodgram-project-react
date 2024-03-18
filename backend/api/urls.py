from rest_framework import routers
from django.urls import path, include

from . import views
from .views import RecipeFavoriteViewSet

router = routers.DefaultRouter()
router.register(r'tags', views.TagViewSet)
router.register(r'ingredients', views.IngredientViewSet)
router.register(r'recipes', views.RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'recipes/<int:id>/favorite/',
        RecipeFavoriteViewSet.as_view(
            {
                'post': 'favorite',
                'delete': 'favorite_delete'
            }
        )
    ),

]
