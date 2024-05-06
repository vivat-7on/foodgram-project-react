from django.db import IntegrityError, transaction
from django.conf import settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated, NotFound, ParseError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from .models import CustomUser, Subscribe
from .serializers import (
    CustomUserSerializer,
    SubscriptionSerializer
)
from api.pagination import CustomPagination


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        return queryset

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=False)
    def subscriptions_list(self, request):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated
        subscribe_queryset = Subscribe.objects.filter(
            subscriber=self.request.user
        )
        if not subscribe_queryset:
            raise NotFound('У вас нет ни одной подписки(')
        users = []
        for sub in subscribe_queryset:
            subscribed_to_id = sub.subscribed_to.id
            users.extend(CustomUser.objects.filter(pk=subscribed_to_id))
        paginator = PageNumberPagination()
        paginator.page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        result_page = paginator.paginate_queryset(users, request)
        recipes_limit = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(
            result_page,
            many=True,
            context={'recipes_limit': recipes_limit,
                     'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscriptions_detail(self, request, id=None):
        subscriber = self.request.user
        if subscriber.id == id:
            raise ParseError('Вы не можете подписаться на себя')
        try:
            subscribed_to = CustomUser.objects.get(pk=id)
            with transaction.atomic():
                Subscribe.objects.create(
                    subscriber=subscriber,
                    subscribed_to=subscribed_to
                )
        except CustomUser.DoesNotExist:
            raise NotFound('Пользователя с таким id не существует')
        except IntegrityError:
            raise ParseError('Подписка уже существует')
        recipes_limit = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(
            subscribed_to,
            context={'recipes_limit': recipes_limit,
                     'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscriptions_delete(self, request, id=None):
        subscriber = self.request.user
        try:
            subscribed_to = CustomUser.objects.get(pk=id)
            with transaction.atomic():
                subscribe = Subscribe.objects.filter(
                    subscriber=subscriber,
                    subscribed_to=subscribed_to
                )
                if not subscribe.exists():
                    raise ParseError("Subscription does not exist")
                subscribe.delete()
        except CustomUser.DoesNotExist:
            raise NotFound
        return Response(status=HTTP_204_NO_CONTENT)
