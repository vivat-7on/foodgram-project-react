from djoser.views import UserViewSet

from .models import CustomUser


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        return queryset

