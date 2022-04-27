from django_filters import rest_framework as filters

from .models.core import Status


class StatusFilter(filters.FilterSet):
    status_group = filters.CharFilter(field_name="status_group__name", lookup_expr='iexact')

    class Meta:
        model = Status
        fields = ['status_group',]
