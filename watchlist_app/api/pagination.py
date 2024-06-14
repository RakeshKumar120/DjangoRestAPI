from rest_framework.pagination import LimitOffsetPagination


class WatchListPagination(LimitOffsetPagination):
    default_limit = 2
    max_limit = 5
    # page_size  = 4