from django.db import transaction, IntegrityError
from django.http import Http404
from rest_framework.decorators import action
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
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import filters

from .serializers import (
    RecipeFavoriteSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
)
from recipes.models import (
    FavoriteRecipe,
    RecipeIngredient, ShoppingCard,
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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

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
        #     result = {}
        #     user = self.request.user
        #     shopping_carts = ShoppingCard.objects.filter(user=user)
        #     for shopping_cart in shopping_carts:
        #         recipes = RecipeIngredient.objects.filter(
        #             recipe=shopping_cart.recipe.id
        #         )
        #         for recipe in recipes:
        #             ingredient = recipe.ingredient
        #             amount = recipe.amount
        #             measurement_unit = recipe.ingredient.measurement_unit
        #             if ingredient in result:
        #                 result[ingredient] = (
        #                     result[ingredient][0] + amount, measurement_unit
        #                 )
        #             else:
        #                 result[ingredient] = (amount, measurement_unit)

        # template = 'recipes/recipe_pdf_template.html'
        # context = {'data_objects': result}
        return generate_pdf(request)


class RecipeShoppingCartView(APIView):
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
