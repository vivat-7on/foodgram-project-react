from django_filters.rest_framework import DjangoFilterBackend


class IngredientFilterBackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')
        if name:
            return queryset.filter(name__istartswith=name)
        return queryset
