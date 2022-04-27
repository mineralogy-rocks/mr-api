from django.db import models
from rest_framework import serializers

from ..models.core import StatusGroup, Status, Country, RelationType
from ..models.mineral import Mineral, MineralStatus, MineralHistory
from .core import StatusListSerializer, CountryListSerializer


class MineralHistorySerializer(serializers.ModelSerializer):

    discovery_year = serializers.CharField()

    class Meta:
        model = MineralHistory
        fields = [
            'id',
            
            'discovery_year',
            'discovery_year_note',
            'first_usage_date',
            'first_known_use',
            ]



class MineralListSerializer(serializers.ModelSerializer):

    formula = serializers.CharField(source='formula_html')
    statuses = StatusListSerializer(many=True)

    discovery_countries = CountryListSerializer(many=True)
    discovery_year = MineralHistorySerializer(source='history')

    class Meta:
        model = Mineral
        fields = [
            'id',
            
            'name',
            'formula',
            'ns_index',
            'statuses',

            'discovery_countries',
            'discovery_year',
            ]


    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get('queryset')

        select_related = [
            'ns_class',
            'ns_subclass',
            'ns_family',

            'history',
        ]

        prefetch_related = [
            models.Prefetch('statuses', Status.objects.select_related('status_group')),
            'discovery_countries',
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset
