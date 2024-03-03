from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
    ModelViewSet
)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import filters

from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeSerializer,
)
from recipes.models import Tag, Ingredient, Recipe


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer
