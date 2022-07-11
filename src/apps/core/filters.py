from email.policy import default

from django.db.models import Case
from django.db.models import Q
from django.db.models import When
from django_filters import rest_framework as filters
from django_filters import widgets

from .models.core import Country
from .models.core import Status
from .models.core import StatusGroup
from .models.ion import Ion
from .models.mineral import Mineral


class StatusFilter(filters.FilterSet):

    status_group = filters.ModelMultipleChoiceFilter(
        label="Status Groups",
        field_name="status_group",
        to_field_name="id",
        queryset=StatusGroup.objects.all(),
    )

    class Meta:
        model = Status
        fields = [
            "status_group",
        ]


class MineralFilter(filters.FilterSet):

    discovery_year__gte = filters.NumberFilter(
        field_name="history__discovery_year_min", lookup_expr="gte"
    )
    discovery_year__lte = filters.NumberFilter(
        field_name="history__discovery_year_max", lookup_expr="lte"
    )
    discovery_year__exact = filters.NumberFilter(
        field_name="history__discovery_year_min", lookup_expr="lte"
    )
    # discovery_countries = filters.ModelMultipleChoiceFilter(
    #     label='Discovery countries',
    #     queryset=Country.objects.all()
    # )
    # filter_group_members = filters.BooleanFilter(field_name='', widget=widgets.BooleanWidget, method='filter_group_members_')

    anion = filters.ModelMultipleChoiceFilter(
        label="Anions",
        field_name="ions_theoretical__ion",
        queryset=Ion.objects.filter(ion_type__name="Anion"),
    )
    cation = filters.ModelMultipleChoiceFilter(
        label="Cations",
        field_name="ions_theoretical__ion",
        queryset=Ion.objects.filter(ion_type__name="Cation"),
    )
    silicate = filters.ModelMultipleChoiceFilter(
        label="Silicates",
        field_name="ions_theoretical__ion",
        queryset=Ion.objects.filter(ion_type__name="Silicate"),
    )
    other_compound = filters.ModelMultipleChoiceFilter(
        label="Other compounds",
        field_name="ions_theoretical__ion",
        queryset=Ion.objects.filter(ion_type__name="Other"),
    )

    class Meta:
        model = Mineral
        fields = [
            "statuses",
            "ns_class",
            "ns_family",
            "anion",
            "cation",
            "silicate",
            "other_compound",
        ]

    def filter_group_members_(self, queryset, name, value):

        discovery_countries = self.data.get("discovery_countries", None)

        if value:
            if discovery_countries:
                queryset = queryset.filter(
                    Q(is_grouping=True)
                    & Q(
                        children_hierarchy__mineral__discovery_countries__in=discovery_countries.split(
                            ","
                        )
                    )
                )

        else:
            if discovery_countries:
                queryset = queryset.filter(
                    Q(discovery_countries__in=discovery_countries.split(","))
                )

        return queryset
