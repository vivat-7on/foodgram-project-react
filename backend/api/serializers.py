import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingCard,
    TagRecipe,
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
    id = serializers.IntegerField(
        source='ingredient.id',
        read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request.method == 'POST':
            data['author'] = CustomUserSerializer(instance.author).data
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        validated_data['author'] = request.user

        recipe = super().create(validated_data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )

        for tag_id in tags_data:
            tag = Tag.objects.get(id=tag_id)
            TagRecipe.objects.create(recipe=recipe, tag=tag)

        return recipe

    def get_tags(self, obj):
        tag_recipes = TagRecipe.objects.filter(
            recipe=obj
        ).select_related('tag')
        tags = [tag_recipe.tag for tag_recipe in tag_recipes]
        return TagSerializer(tags, many=True).data

    def get_ingredients(self, obj):
        ingredients_recipes = RecipeIngredient.objects.filter(
            recipe=obj
        ).select_related('ingredient')
        ingredient_data = RecipeIngredientSerializer(ingredients_recipes,
                                                     many=True).data
        return ingredient_data

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
