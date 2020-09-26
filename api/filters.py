from django_filters import rest_framework as filters
from .models import Title
from rest_framework.filters import SearchFilter

class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class TitleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    year = filters.NumberFilter()
    category = filters.NumberFilter()
    genre = CharFilterInFilter(field_name='genre__slug', lookup_expr='in')

    class Meta:
        models = Title
        fields = ['category', 'year', 'name', 'genre']
