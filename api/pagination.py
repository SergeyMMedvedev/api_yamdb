from rest_framework.pagination import PageNumberPagination


class NumberPagination(PageNumberPagination):
    page_size = 5