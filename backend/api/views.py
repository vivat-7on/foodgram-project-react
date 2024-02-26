from rest_framework import viewsets

from .recipes.models import Tag
from .serializers import TagSerializer


class TagViewSet(viewsets.ViewSet):
    queryset = Tag.objects.all()
    serializer = TagSerializer()
