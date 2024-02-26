from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

router = DefaultRouter()
router.register('', CustomUserViewSet, basename='users')

urlpatterns = router.urls

