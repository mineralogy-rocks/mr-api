from django.db import models
from django.db.models import Q, Count, F
from rest_framework import serializers

from ..models.core import Status
from ..models.crystal import CrystalSystem
from ..models.mineral import Mineral, MineralStatus, MineralHistory, MineralCrystallography, MineralHierarchy
from .core import StatusListSerializer, CountryListSerializer
from .crystal import CrystalSystemSerializer, CrystalSystemsStatsSerializer
from .base import BaseSerializer


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
    crystal_systems = CrystalSystemSerializer(many=True)

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
            'crystal_systems',
            'statuses',
            'relations',

            'discovery_countries',
            'history'
            ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get('queryset')
        request = kwargs.get('request')

        select_related = [
            'history',
        ]

        prefetch_related = [
            models.Prefetch('statuses', Status.objects.select_related('status_group')),
            models.Prefetch('crystal_systems', CrystalSystem.objects.all().distinct()),
            'discovery_countries',
        ]
        
        for query_param in request.query_params.keys():
            
            if query_param in ['anions', 'cations', 'silicates', 'other_compounds']:
                prefetch_related.append('ions_theoretical')

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


    def get_crystal_systems(self, instance):
        if (instance.is_grouping):
            crystal_systems = instance.children_hierarchy.values('mineral__crystal_systems') \
                                                         .annotate(
                                                            id=F('mineral__crystal_systems__id'),
                                                            name=F('mineral__crystal_systems__name'),
                                                            count=Count('mineral', distinct=True)
                                                          ) \
                                                          .filter(Q(mineral__crystal_systems__isnull=False))

            return crystal_systems.values('id', 'name', 'count')
        
        return CrystalSystemSerializer(instance.crystal_systems, many=True).data 


    def to_representation(self, instance):
        output = super().to_representation(instance)

        return output
