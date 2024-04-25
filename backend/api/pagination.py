from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(LimitOffsetPagination):
    default_limit = 6
    max_limit = 100
