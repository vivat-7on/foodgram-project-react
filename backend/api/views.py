from django.db import transaction, IntegrityError
from django.http import Http404
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST
)
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
    ModelViewSet,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework import filters, status

from .filters import IngredientFilterBackend
from .pagination import CustomPagination
from .serializers import (
    RecipeFavoriteSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
)
from recipes.models import (
    FavoriteRecipe,
    RecipeIngredient,
    ShoppingCard,
    Ingredient,
    Recipe,
    Tag,
)
from .utils import generate_pdf


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
    queryset = Recipe.objects.all()
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
            queryset = queryset.filter(tags__slug__in=tags)

        is_favorited = self.request.query_params.get('is_favorited', '0')
        try:
            if is_favorited == '1' and self.request.user.is_authenticated:
                favorited_recipes = FavoriteRecipe.objects.filter(
                    user=self.request.user
                ).values_list('recipe_id', flat=True)
                queryset = queryset.filter(id__in=favorited_recipes)
        except (ValueError, TypeError) as e:
            raise ParseError(detail='Invalid value for is_favorited')

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', '0')
        try:
            if is_in_shopping_cart == '1' \
                    and self.request.user.is_authenticated:
                shopping_cart_recipes = ShoppingCard.objects.filter(
                    user=self.request.user
                ).values_list('recipe_id', flat=True)
                queryset = queryset.filter(id__in=shopping_cart_recipes)
        except (ValueError, TypeError) as e:
            raise ParseError(detail='Invalid value for is_in_shopping_cart')
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeFavoriteViewSet(ModelViewSet):

    @action(detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, id=None):
        try:
            recipe = get_object_or_404(Recipe, pk=id)
            with transaction.atomic():
                FavoriteRecipe.objects.create(
                    recipe=recipe,
                    user=self.request.user
                )
        except IntegrityError:
            return Response(
                {'error': 'Этот рецепт уже в вашем списке.'},
                status=HTTP_400_BAD_REQUEST
            )
        except Http404:
            return Response(
                {'error': 'Такого рецепта нет.'},
                status=HTTP_400_BAD_REQUEST
            )
        serializer = RecipeFavoriteSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def favorite_delete(self, request, id=None):
        user = self.request.user
        try:
            recipe = get_object_or_404(Recipe, pk=id)
            with transaction.atomic():
                FavoriteRecipe.objects.filter(
                    recipe=recipe,
                    user=user
                ).delete()
        except Http404:
            return Response(
                {'error': 'Такого рецепта нет.'},
                status=HTTP_400_BAD_REQUEST
            )
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {'error': 'Такого рецепта нет.'},
                status=HTTP_400_BAD_REQUEST
            )

        return Response(status=HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):
    def get(self, request):
        result = {}
        user = self.request.user
        shopping_carts = ShoppingCard.objects.filter(user=user)
        for shopping_cart in shopping_carts:
            recipes = RecipeIngredient.objects.filter(
                recipe=shopping_cart.recipe.id
            )
            for recipe in recipes:
                ingredient = str(recipe.ingredient)
                amount = recipe.amount
                measurement_unit = recipe.ingredient.measurement_unit
                if ingredient in result:
                    result[ingredient] = (
                        result[ingredient][0] + amount, measurement_unit
                    )
                else:
                    result[ingredient] = (amount, measurement_unit)

        template = 'recipes/recipe_pdf_template.html'
        context = {'data_objects': result}
        html_doc = render(request, template, context)
        return generate_pdf(request, html_doc.content)
        # return render(request, template, context)


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
            return Response(
                {'error': 'Этот рецепт уже в вашем списке покупок.'},
                status=HTTP_400_BAD_REQUEST
            )
        except Http404:
            return Response(
                {'error': 'Такого рецепта нет.'},
                status=HTTP_400_BAD_REQUEST
            )
        serializer = RecipeFavoriteSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete(self, request, id=None):
        user = self.request.user
        try:
            recipe = get_object_or_404(Recipe, pk=id)
            with transaction.atomic():
                ShoppingCard.objects.filter(
                    recipe=recipe,
                    user=user
                ).delete()
        except Http404:
            return Response(
                {'error': 'Такого рецепта нет.'},
                status=HTTP_400_BAD_REQUEST
            )
        except ShoppingCard.DoesNotExist:
            return Response(
                {'error': 'Такого рецепта нет.'},
                status=HTTP_400_BAD_REQUEST
            )

        return Response(status=HTTP_204_NO_CONTENT)
