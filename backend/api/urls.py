from rest_framework import routers
from django.urls import path, include

from . import views
from .views import RecipeFavoriteViewSet

router = routers.DefaultRouter()
router.register(r'tags', views.TagViewSet)
router.register(r'ingredients', views.IngredientViewSet)
router.register(r'recipes', views.RecipeViewSet)

urlpatterns = [
    path(
        'recipes/<int:id>/favorite/',
        RecipeFavoriteViewSet.as_view(
            {
                'post': 'favorite',
                'delete': 'favorite_delete'
            }
        )
    ),
    path(
        'recipes/download_shopping_cart/',
        views.DownloadShoppingCartView.as_view(),
        name='download_shopping_cart'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        views.RecipeShoppingCartView.as_view(),
        name='recipe_shopping_cart'
    ),
    path('', include(router.urls)),
]
