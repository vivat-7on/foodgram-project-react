from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import IntegrityError, transaction
from rest_framework.status import HTTP_204_NO_CONTENT

from .models import CustomUser, Subscribe
from .serializers import (
    CustomUserSerializer,
    SubscriptionSerializer
)


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        return queryset

    @action(detail=False)
    def subscriptions_list(self, request):
        subscribe_queryset = Subscribe.objects.filter(
            subscriber=self.request.user
        )
        if not subscribe_queryset:
            return HttpResponse(
                'Вы не подписанны ни на одного автора.')
        for sub in subscribe_queryset:
            subscribed_to_id = sub.subscribed_to.id
            users = CustomUser.objects.filter(pk=subscribed_to_id)
            paginator = PageNumberPagination()
            paginator.page_size = 3
            result_page = paginator.paginate_queryset(users, request)
            serializer = SubscriptionSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscriptions_detail(self, request, id=None):
        subscriber = self.request.user
        try:
            subscribed_to = CustomUser.objects.get(pk=id)
            with transaction.atomic():
                Subscribe.objects.create(
                    subscriber=subscriber,
                    subscribed_to=subscribed_to
                )
        except CustomUser.DoesNotExist:
            return Response(
                'Автор не найден.',
                status=500
            )
        except IntegrityError:
            return Response(
                'Вы уже подписанны на этого автора.',
                status=500
            )
        subscribed_to.is_subscribed = True
        serializer = SubscriptionSerializer(subscribed_to)
        return Response(serializer.data)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscriptions_delete(self, request, id=None):
        subscriber = self.request.user
        try:
            subscribed_to = CustomUser.objects.get(pk=id)
            with transaction.atomic():
                Subscribe.objects.filter(
                    subscriber=subscriber,
                    subscribed_to=subscribed_to
                ).delete()
        except CustomUser.DoesNotExist:
            return Response(
                'Автор не найден.',
                status=500
            )
        subscribed_to.is_subscribed = False
        return Response(status=HTTP_204_NO_CONTENT)
