from django.db import models
from rest_framework import serializers

from ..models.core import StatusGroup, Status, Country, RelationType, NsFamily
from ..models.mineral import Mineral, MineralStatus, MineralHistory
from .core import StatusListSerializer, CountryListSerializer
from .crystal import CrystalSystemSerializer, CrystalSystemsStatsSerializer


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

    ns_index = serializers.CharField(source='ns_index_')
    formula = serializers.CharField(source='formula_html')
    crystal_system = CrystalSystemSerializer(source='crystal.crystal_system')
    statuses = StatusListSerializer(many=True)

    relations = serializers.JSONField(source='relations_')

    discovery_countries = CountryListSerializer(many=True)
    
    history = serializers.JSONField(source='history_')

    class Meta:
        model = Mineral
        fields = [
            'id',
            
            'name',
            'ns_index',
            'formula',
            'crystal_system',
            'statuses',

            'relations',

            'discovery_countries',
            'history'
            ]
        
    def __init__(self, instance, *args, **kwargs):
        print(instance)
        super().__init__(instance, *args, **kwargs)

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get('queryset')
        request = kwargs.get('request')

        select_related = [
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
