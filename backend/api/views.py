from rest_framework import viewsets
from rest_framework.response import Response

from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
)
from recipes.models import Tag, Ingredient, Recipe


class TagIngredientViewSetMixin(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(TagIngredientViewSetMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(TagIngredientViewSetMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
