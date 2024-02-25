from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import CustomUser


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        write_only_fields = ('password',)


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed']
