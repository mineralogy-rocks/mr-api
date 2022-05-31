from django.db import models
from rest_framework import serializers

from ..models.core import StatusGroup, Status, Country, RelationType, NsFamily
from ..models.mineral import Mineral, MineralStatus, MineralHistory
from .core import StatusListSerializer, CountryListSerializer
from .crystal import CrystalSystemSerializer


class MineralHistorySerializer(serializers.ModelSerializer):

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
    crystal_system = CrystalSystemSerializer(source='crystal.crystal_system')
    statuses = StatusListSerializer(many=True)

    isostructural_minerals_count = serializers.IntegerField()
    varieties_count = serializers.IntegerField()
    polytypes_count = serializers.IntegerField()

    discovery_countries = CountryListSerializer(many=True)
    discovery_year = MineralHistorySerializer(source='history')

    class Meta:
        model = Mineral
        fields = [
            'id',
            
            'name',
            'formula',
            'crystal_system',
            'ns_index',
            'statuses',

            'isostructural_minerals_count',
            'varieties_count',
            'polytypes_count',

            'discovery_countries',
            'discovery_year',
            ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get('queryset')
        request = kwargs.get('request')

        select_related = [
            'ns_class',
            'ns_subclass',
            'ns_family',

            'history',
            'crystal__crystal_system',
        ]

        prefetch_related = [
            models.Prefetch('statuses', Status.objects.select_related('status_group')),
            'discovery_countries',
        ]
        
        for query_param in request.query_params.keys():
            
            if query_param in ['anions', 'cations', 'silicates', 'other_compounds']:
                prefetch_related.append('ions_theoretical')

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset
