import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCard, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
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
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=['ingredient', 'recipes']
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=True,
        allow_null=True,
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

    def _is_related_to_user(self, obj, model):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return model.objects.filter(
                recipe=obj,
                user=request.user
            ).exists()
        return False

    def get_is_favorited(self, obj):
        return self._is_related_to_user(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        return self._is_related_to_user(obj, ShoppingCard)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': ':Добавьте хотябы один ингредиент!'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient_id = ingredient_item.get('id')
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиент с id {ingredient_id} '
                                   f'не существует!'
                })

            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными!'
                )
            if int(ingredient_item['amount']) < 1:
                raise serializers.ValidationError({
                    'ingredients': (
                        'Количество ингредиента должно быть больше нуля!'
                    )
                })
            ingredient_list.append(ingredient)
        data['ingredients'] = ingredients

        tags = self.initial_data.get('tags')

        if not tags:
            raise serializers.ValidationError({
                'tags': ':Добавьте хотябы один тег!'})
        tags_list = []
        for tag_id in tags:
            try:
                Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise serializers.ValidationError({
                    'tags': f'Тег с id {tag_id} не существует!'
                })

            tags_list.append(tag_id)

        if len(set(tags_list)) != len(tags_list):
            raise serializers.ValidationError('Теги должны быть уникальными!')

        data['tags'] = tags_list
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            ingredient_obj = get_object_or_404(Ingredient, pk=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient_obj,
            )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.pop('ingredients')
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            ingredient_obj = get_object_or_404(Ingredient, pk=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=instance,
                amount=ingredient['amount'],
                ingredient=ingredient_obj,
            )
        instance.save()
        return instance


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]
