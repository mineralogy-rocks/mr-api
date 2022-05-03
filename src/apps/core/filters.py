from django_filters import rest_framework as filters

from .models.core import Status, StatusGroup
from .models.ion import Ion
from .models.mineral import Mineral


class StatusFilter(filters.FilterSet):

    status_group = filters.ModelMultipleChoiceFilter(
        label='Status Groups',
        field_name="status_group__name", 
        to_field_name='name',
        queryset=StatusGroup.objects.all()
        )

    class Meta:
        model = Status
        fields = ['status_group',]



class MineralFilter(filters.FilterSet):

    discovery_year__gte = filters.NumberFilter(field_name='history__discovery_year_min', lookup_expr='gte')
    discovery_year__lte = filters.NumberFilter(field_name='history__discovery_year_max', lookup_expr='lte')
    discovery_year__exact = filters.NumberFilter(field_name='history__discovery_year_min', lookup_expr='lte')

    anion = filters.ModelMultipleChoiceFilter(
            label='Anions',
            field_name='ions_theoretical', 
            queryset=Ion.objects.filter(ion_type__name='Anion')
        )
    cation = filters.ModelMultipleChoiceFilter(
            label='Cations',
            field_name='ions_theoretical', 
            queryset=Ion.objects.filter(ion_type__name='Cation')
        )
    silicate = filters.ModelMultipleChoiceFilter(
            label='Silicates',
            field_name='ions_theoretical', 
            queryset=Ion.objects.filter(ion_type__name='Silicate')
        )
    other_compound = filters.ModelMultipleChoiceFilter(
            label='Other compounds',
            field_name='ions_theoretical', 
            queryset=Ion.objects.filter(ion_type__name='Other')
        )

    class Meta:
        model = Mineral
        fields = [
            'statuses',

            'ns_class',
            'ns_family',

            'discovery_countries',

            'anion',
            'cation',
            'silicate',
            'other_compound',
            ]
