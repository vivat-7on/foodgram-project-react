from rest_framework.viewsets import (
    ReadOnlyModelViewSet
)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import filters

from .serializers import (
    TagSerializer,
    IngredientSerializer,
    # RecipeSerializer,
)
from recipes.models import Tag, Ingredient, Recipe

from recipes.models import RecipeIngredient, TagRecipe


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



# class RecipeViewSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#
#     def create(self, request, *args, **kwargs):
#         ingredients_data = request.data.pop('ingredients', [])
#         tags_data = request.data.pop('tags', [])
#
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         self.perform_create(serializer, ingredients_data, tags_data)
#
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED,
#                         headers=headers)
#
#     def perform_create(self, serializer, ingredients_data, tags_data):
#         instance = serializer.save()
#
#         for ingredient_data in ingredients_data:
#             ingredient = Ingredient.objects.get(id=ingredient_data['id'])
#             RecipeIngredient.objects.create(
#                 recipe=instance,
#                 ingredient=ingredient,
#                 amount=ingredient_data['amount']
#             )
#
#         for tag_id in tags_data:
#             tag = Tag.objects.get(id=tag_id)
#             TagRecipe.objects.create(recipe=instance, tag=tag)
