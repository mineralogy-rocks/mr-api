# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models import Q, Count, F, OuterRef, Subquery, Value
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

    ns_index = serializers.CharField(source='ns_index_')
    formula = serializers.CharField(source='formula_html')
    ions = serializers.SerializerMethodField()
    crystal_systems = serializers.SerializerMethodField()

    # statuses = serializers.JSONField(source='statuses_')
    # crystal_systems = serializers.JSONField(source='crystal_systems_')
    # colors = serializers.JSONField(source='colors_')
    # relations = serializers.JSONField(source='relations_')
    # discovery_countries = serializers.JSONField(source='discovery_countries_')
    # history = serializers.JSONField(source='history_')

    class Meta:
        model = Mineral
        fields = [
            'id',
            
            'name',
            'ns_index',
            'formula',
            'ions',
            'crystal_systems',
            # 'colors',
            
            # 'statuses',
            # 'relations',
            # 'discovery_countries',
            # 'history'
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
            models.Prefetch('crystal_systems', CrystalSystem.objects.filter(Q(minerals__mineral__parents_hierarchy__parent__in=queryset.values('id'))).distinct(),
                            to_attr='crystal_system_counts'
                            ),
            # models.Prefetch('crystallography', MineralCrystallography.objects.filter(Q(mineral__parents_hierarchy__parent__in=queryset.values('id'))) \
            #                                                                  .select_related('crystal_system') \
            #                                                                  .annotate(
            #                                                                     crystal_systems_=JSONObject(
            #                                                                         id=F('crystal_system__id'),
            #                                                                         name=F('crystal_system__name'),
            #                                                                         count=Count('mineral', distinct=True)
            #                                                                     )
            #                                                                  ) \
            #                                                                  .defer('crystal_class', 'space_group', 'a', 'b', 'c', 'alpha', 'gamma', 'z'),
            #                                                                  to_attr='crystal_system_counts'
            #                                                                  ),
            models.Prefetch('ions', MineralIonPosition.objects.select_related('ion', 'position').order_by('position', 'ion__formula'), to_attr='positions'),
            'discovery_countries',
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


    def get_crystal_systems(self, instance):
        # if instance.is_grouping:
                                                               
        print(instance.crystal_system_counts)
        return []
        # return CrystalSystemSerializer(instance.crystal_systems, many=True).data
