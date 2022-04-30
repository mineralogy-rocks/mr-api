from django_filters import rest_framework as filters

from .models.core import Status
from .models.ion import Ion
from .models.mineral import Mineral


class StatusFilter(filters.FilterSet):

    status_group = filters.CharFilter(field_name="status_group__name", lookup_expr='iexact')

    class Meta:
        model = Status
        fields = ['status_group',]



class MineralFilter(filters.FilterSet):

    discovery_year_min = filters.NumberFilter(field_name="history__discovery_year_min", lookup_expr='gte')
    discovery_year_max = filters.NumberFilter(field_name="history__discovery_year_max", lookup_expr='lte')

    anions = filters.ModelMultipleChoiceFilter(
        label='Anions',
        field_name='ions_theoretical', 
        queryset=Ion.objects.filter(ion_type__name='Anion')
        )
    cations = filters.ModelMultipleChoiceFilter(
        label='Cations',
        field_name='ions_theoretical', 
        queryset=Ion.objects.filter(ion_type__name='Cation')
        )
    silicates = filters.ModelMultipleChoiceFilter(
        label='Silicates',
        field_name='ions_theoretical', 
        queryset=Ion.objects.filter(ion_type__name='Silicate')
        )
    other_compounds = filters.ModelMultipleChoiceFilter(
        label='Other compounds',
        field_name='ions_theoretical', 
        queryset=Ion.objects.filter(ion_type__name='Other')
        )

    class Meta:
        model = Mineral
        fields = [
            'statuses',

            'ns_class',

            'discovery_year_min',
            'discovery_year_max',
            'discovery_countries',

            'anions',
            'cations',
            'silicates',
            'other_compounds',
            ]
