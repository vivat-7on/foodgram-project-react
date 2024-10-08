import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe
from .models import CustomUser, Subscribe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        ]
        write_only_fields = ('password',)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            if self.context['request'].path == '/users/me':
                return False
            else:
                subscribed = Subscribe.objects.filter(
                    subscriber=self.context['request'].user,
                    subscribed_to=obj
                )
                return subscribed.exists()
        else:
            return False


class RecipeSubscribeSerializer(ModelSerializer):
    image = Base64ImageField(
        required=False,
        allow_null=True,
    )

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
    is_subscribed = serializers.SerializerMethodField()

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
        recipes_limit = self.context.get('recipes_limit', None)
        if recipes_limit is not None:
            return RecipeSubscribeSerializer(
                queryset[:int(recipes_limit)],
                many=True
            ).data
        return RecipeSubscribeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.id).count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if request is not None:
            return Subscribe.objects.filter(
                subscriber=request.user,
                subscribed_to=obj.id
            ).exists()
        return False
