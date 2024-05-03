from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponse
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import (AuthenticationFailed, NotFound,
                                       ParseError, PermissionDenied)
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCard, Tag)

from .filters import IngredientFilterBackend
from .pagination import CustomPagination
from .serializers import (IngredientSerializer, RecipeFavoriteSerializer,
                          RecipeSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilterBackend,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related('tags')
    serializer_class = RecipeSerializer
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ['author__id', 'tags__name']
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset = queryset.filter(author__id=author)

        tags = self.request.query_params.getlist('tags', [])
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        is_favorited = self.request.query_params.get('is_favorited', '0')
        try:
            if is_favorited == '1' and self.request.user.is_authenticated:
                favorited_recipes = FavoriteRecipe.objects.filter(
                    user=self.request.user
                ).values_list('recipe_id', flat=True)
                queryset = queryset.filter(id__in=favorited_recipes)
        except (ValueError, TypeError):
            raise ParseError(detail='Invalid value for is_favorited')

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', '0')
        try:
            if (is_in_shopping_cart == '1'
                    and self.request.user.is_authenticated):
                shopping_cart_recipes = ShoppingCard.objects.filter(
                    user=self.request.user
                ).values_list('recipe_id', flat=True)
                queryset = queryset.filter(id__in=shopping_cart_recipes)
        except (ValueError, TypeError):
            raise ParseError(detail='Invalid value for is_in_shopping_cart')
        return queryset

    def update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if user != instance.author:
            raise PermissionDenied

        ingredients = request.data.get('ingredients')
        tags = request.data.get('tags')

        if not (ingredients and tags):
            raise ParseError("Ingredient and tags are required.")

        instance.tags.set(tags)

        if ingredients:
            for ingredient_data in ingredients:
                ingredient_id = ingredient_data['id']
                ingredient_obj = get_object_or_404(Ingredient,
                                                   pk=ingredient_id)
                (
                    recipe_ingredient, created
                ) = RecipeIngredient.objects.get_or_create(
                    recipe=instance,
                    ingredient=ingredient_obj,
                    defaults={'amount': ingredient_data['amount']}
                )

                if not created:
                    recipe_ingredient.amount = ingredient_data['amount']
                    recipe_ingredient.save()

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if user != instance.author:
            raise PermissionDenied
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeFavoriteViewSet(ModelViewSet):

    @action(detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, id=None):
        if not request.user.is_authenticated:
            raise AuthenticationFailed
        try:
            recipe = get_object_or_404(Recipe, pk=id)
            if FavoriteRecipe.objects.filter(
                    recipe=recipe,
                    user=self.request.user
            ).exists():
                raise ParseError
            with transaction.atomic():
                FavoriteRecipe.objects.create(
                    recipe=recipe,
                    user=self.request.user
                )
        except Http404:
            raise ParseError
        serializer = RecipeFavoriteSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def favorite_delete(self, request, id=None):
        user = self.request.user
        if not user.is_authenticated:
            raise AuthenticationFailed
        try:
            recipe = get_object_or_404(Recipe, pk=id)
            with transaction.atomic():
                favorite_recipe = FavoriteRecipe.objects.filter(
                    recipe=recipe,
                    user=user
                )
                if not favorite_recipe.exists():
                    raise ParseError
                favorite_recipe.delete()
        except Http404:
            raise NotFound
        return Response(status=HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):
    def get(self, request):
        ing_am_un = {}
        user = self.request.user
        shopping_carts = ShoppingCard.objects.filter(user=user)
        for shopping_cart in shopping_carts:
            recipes = RecipeIngredient.objects.filter(
                recipe=shopping_cart.recipe.id
            )
            for recipe in recipes:
                ingredient = recipe.ingredient
                if ingredient is not None:
                    try:
                        ingredient_str = str(ingredient)
                    except Exception as e:
                        ingredient_str = f'Error {e}'
                        amount = recipe.amount
                    measurement_unit = recipe.ingredient.measurement_unit
                    if ingredient_str in ing_am_un:
                        ing_am_un[ingredient_str] = (
                            ing_am_un[ingredient_str][0] + amount,
                            measurement_unit
                        )
                    else:
                        ing_am_un[ingredient_str] = (amount, measurement_unit)
        content = ""
        for ingredient, (amount, measurement_unit) in ing_am_un.items():
            content += f"{ingredient}: {amount} {measurement_unit}\n"

        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response


class RecipeShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            recipe = get_object_or_404(Recipe, pk=id)
            with transaction.atomic():
                ShoppingCard.objects.create(
                    recipe=recipe,
                    user=self.request.user
                )
        except IntegrityError:
            raise ParseError
        except Http404:
            raise ParseError
        serializer = RecipeFavoriteSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete(self, request, id=None):
        user = self.request.user
        try:
            recipe = get_object_or_404(Recipe, pk=id)
            with transaction.atomic():
                shopping_card = ShoppingCard.objects.filter(
                    recipe=recipe,
                    user=user
                )
                if not shopping_card.exists():
                    raise ParseError
                shopping_card.delete()
        except Http404:
            raise NotFound
        return Response(status=HTTP_204_NO_CONTENT)
