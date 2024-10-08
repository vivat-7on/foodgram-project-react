import base64

from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import CustomUserSerializer
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCard, Tag)


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
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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
        fields = ('id', 'name', 'measurement_unit', 'amount')
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
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)]
    )

    class Meta:
        model = Recipe
        fields = (
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
        )

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

    def validate_ingredients(self, data):
        ingredients_data = self.initial_data.get('ingredients', [])
        if not ingredients_data:
            raise serializers.ValidationError({
                'ingredients': 'Добавьте хотя бы один ингредиент!'
            })

        ingredient_ids = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными!'
                })
            ingredient_ids.append(ingredient_id)

            try:
                Ingredient.objects.get(pk=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError({
                    'ingredients': (f'Ингредиент с '
                                    f'id={ingredient_id} не существует!')
                })
            amount = ingredient_data.get('amount', 0)
            if amount < 1:
                raise serializers.ValidationError({
                    'ingredients': ('Значение measurement_unit должно быть '
                                    'больше или равно 1!')
                })
            ingredient_data['measurement_unit'] = amount
        return ingredients_data

    def validate_tags(self, data):
        tags_data = self.initial_data.get('tags', [])
        if not tags_data:
            raise serializers.ValidationError({
                'tags': 'Добавьте хотя бы один тег!'
            })

        tag_ids = []
        for tag_id in tags_data:
            if tag_id in tag_ids:
                raise serializers.ValidationError({
                    'tags': 'Теги должны быть уникальными!'
                })
            tag_ids.append(tag_id)

            try:
                Tag.objects.get(pk=tag_id)
            except Tag.DoesNotExist:
                raise serializers.ValidationError({
                    'tags': f'Тег с id={tag_id} не существует!'
                })
        return tags_data

    def validate(self, data):
        ingredients = self.validate_ingredients(data)
        tags = self.validate_tags(data)
        data['ingredients'] = ingredients
        data['tags'] = tags
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = []
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        ingredient_objs = Ingredient.objects.in_bulk(ingredient_ids)
        for ingredient in ingredients:
            ingredient_obj = ingredient_objs.get(ingredient['id'])
            if ingredient_obj:
                recipe_ingredients.append(RecipeIngredient(
                    recipe=recipe,
                    amount=ingredient['amount'],
                    ingredient=ingredient_obj,
                ))

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'ingredients' in validated_data:
            ingredients = self.validate_ingredients(validated_data)
            RecipeIngredient.objects.filter(recipe=instance).delete()
            ingredient_ids = [ingredient['id'] for ingredient in ingredients]
            ingredient_objs = Ingredient.objects.in_bulk(ingredient_ids)
            for ingredient in ingredients:
                ingredient_obj = ingredient_objs.get(ingredient['id'])
                if ingredient_obj:
                    RecipeIngredient.objects.create(
                        recipe=instance,
                        amount=ingredient['amount'],
                        ingredient=ingredient_obj,
                    )
        if 'tags' in validated_data:
            tags = self.validate_tags(validated_data)
            instance.tags.clear()
            for tag_id in tags:
                tag = Tag.objects.get(pk=tag_id)
                instance.tags.add(tag)

        instance.save()
        return instance


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
