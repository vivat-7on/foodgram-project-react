from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from recipes.models import Recipe
from .models import CustomUser, Subscribe


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]
        write_only_fields = ('password',)


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]


class RecipeSubscribeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]


class SubscriptionSerializer(ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',

        ]

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.id)
        return RecipeSubscribeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.id).count()
