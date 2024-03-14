from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import CustomUser, Subscribe
from .serializers import SubscriptionSerializer


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        return queryset

    @action(detail=False, pagination_class=[PageNumberPagination])
    def subscriptions_list(self, request):
        subscribe_queryset = Subscribe.objects.filter(
            subscriber=self.request.user
        )
        for sub in subscribe_queryset:
            subscribed_to_id = sub.subscribed_to.id
            users = CustomUser.objects.filter(pk=subscribed_to_id)
            paginator = PageNumberPagination()
            paginator.page_size = 1
            result_page = paginator.paginate_queryset(users, request)
            serializer = SubscriptionSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

    @action(detail=True)
    def subscriptions_detail(self, request, id=None):
        return Response({'pk=': id})
