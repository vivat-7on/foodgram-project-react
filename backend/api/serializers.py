from djoser.serializers import UserCreateSerializer, TokenCreateSerializer

from users.models import CustomUser


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        write_only_fields = ('password',)

#
# class CustomTokenCreateSerializer(TokenCreateSerializer):
