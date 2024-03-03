import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    FavoriteRecipe,
    ShoppingCard,
    RecipeIngredient,
)

from users.serializers import CustomUserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
        read_only=True
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeListSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_is_favorited(self, obj):
        return self._is_related_to_user(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        return self._is_related_to_user(obj, ShoppingCard)

    def _is_related_to_user(self, obj, model):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return model.objects.filter(
                recipe=obj,
                user=request.user
            ).exists()
        return False
