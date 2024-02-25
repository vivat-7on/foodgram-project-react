from django.urls import path, include
from rest_framework import routers
from django.conf.urls.static import static

from django.conf import settings

router = routers.DefaultRouter()

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
