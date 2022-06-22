# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models import Q, Count, F, OuterRef, Subquery, Value, Case, When
from django.db.models.functions import JSONObject
from rest_framework import serializers

from ..models.core import Status
from ..models.crystal import CrystalSystem
from ..models.mineral import Mineral, MineralStatus, MineralHistory, MineralCrystallography, MineralHierarchy, MineralIonPosition
from ..models.ion import IonPosition, Ion
from .core import StatusListSerializer, CountryListSerializer
from .crystal import CrystalSystemSerializer, CrystalSystemsStatsSerializer
from .base import BaseSerializer
from .ion import MineralIonPositionSerializer, IonPrimitiveSerializer


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

    url = serializers.URLField(source='get_absolute_url')
    ns_index = serializers.CharField(source='ns_index_')
    formula = serializers.CharField(source='formula_html')
    is_grouping = serializers.BooleanField()
    groups = serializers.HyperlinkedRelatedField(
        source='get_groups_urls',
        many=True,
        read_only=True,
        view_name='core:mineral-detail'
    )
    
    crystal_systems = serializers.JSONField(source='crystal_systems_')
    ions = serializers.JSONField(source='ions_')

    statuses = serializers.JSONField(source='statuses_')
    colors = serializers.JSONField(source='colors_')
    relations = serializers.JSONField(source='relations_')
    discovery_countries = serializers.JSONField(source='discovery_countries_')
    history = serializers.JSONField(source='history_')

    class Meta:
        model = Mineral
        fields = [
            'id',
            
            'name',
            'url',
            'ns_index',
            'formula',
            'is_grouping',
            'groups',
            
            'ions',
            'crystal_systems',
            'colors',
            
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
            # models.Prefetch('crystal_systems', CrystalSystem.objects.all().distinct()),
            
            # models.Prefetch('children_hierarchy', MineralHierarchy.objects.select_related('mineral') \
            #                                                               .prefetch_related(
            #                                                                   models.Prefetch('mineral__crystal_systems', CrystalSystem.objects.all().distinct())
            #                                                                ),
            #                 to_attr='children'
            #                 ),
            
            # models.Prefetch('ions', MineralIonPosition.objects.select_related('ion', 'position').order_by('position', 'ion__formula'), 
            #                 to_attr='positions'),
            # 'discovery_countries',
            'parents_hierarchy',
        ]
        
        for query_param in request.query_params.keys(): 
            
            if query_param in ['anions', 'cations', 'silicates', 'other_compounds']:
                prefetch_related.append('ions_theoretical')

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


    def get_ions(self, instance):
        output = MineralIonPositionSerializer(instance.positions, many=True).data
        
        output_ = []
        positions_ = []
        
        for ion in output:
            position_ = ion['position']
            if position_['id'] not in positions_:
                positions_.append(position_['id'])
                output_.append({
                    'position': position_,
                    'ions': [ion_['ion'] for ion_ in output if ion_['position']['id'] == position_['id']]
                })

        return output_
