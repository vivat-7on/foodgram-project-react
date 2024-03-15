from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import CustomUserViewSet

router = SimpleRouter()
router.register('', CustomUserViewSet, basename='users')

urlpatterns = [
    path(
        'subscriptions/',
        CustomUserViewSet.as_view({'get': 'subscriptions_list'}),
        name='user-subscriptions-list'
    ),
    path(
        '<int:id>/subscriptions/',
        CustomUserViewSet.as_view({
            'post': 'subscriptions_detail',
            'delete': 'subscriptions_delete'
        }),
        name='user-subscriptions-detail'
    ),
]

urlpatterns += router.urls
