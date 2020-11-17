from django_filters import rest_framework as filters
from titles.models import Title


class TitleFilter(filters.FilterSet):
    """
    Фильтр по полю slug у связанных таблиц Category и Genre, а так же по полю
    name таблицы Title без учета регистра.
    """
    genre = filters.CharFilter(field_name='genre__slug')
    category = filters.CharFilter(field_name='category__slug')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'name', 'year',)
