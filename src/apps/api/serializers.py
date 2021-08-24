from rest_framework import serializers
from django.db.models import Q, F, Case, When, BooleanField, Subquery, Value, Min, Exists, Count
from decimal import *

from api.models import *
from api import services as services
from stats.serializers import discoveryCountryCountsSerializer
from stats.functions.stats import discovery_country_counts


class StatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusList
        fields = ['status_id', 'description_short', 'description_long']

class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryList
        fields = ['country_name', 'region']

class RelationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationList
        fields = ['type', 'note']


class MineralStatusSerializer(serializers.ModelSerializer):
    status = StatusListSerializer(source='status_id_set', read_only=True, many=True)
    description_short = serializers.CharField(read_only=True)
    description_long = serializers.CharField(read_only=True)

    class Meta:
        model = MineralStatus
        fields = ['status', 'status_id', 'description_short', 'description_long']

class StatusDescriptionSerializer(serializers.ModelSerializer):

    group = serializers.SerializerMethodField()
    # description = 
    # relations = 

    class Meta:
        model = StatusList
        fields = ['group']
        
    

    def get_group(self, instance):
        """ Grab all 

        Args:
            instance (QuerySet object): a manager for mineral_status through MineralLog object

        Returns:
            [type]: [description]
        """

        relations = services.get_relations(instance)
        # print(relations.values())

        return {'some': relations.values_list()}

# class StatusDescriptionSerializer(serializers.BaseSerializer):

#     def get_status_description(self, mineral_id):

#         # TODO: refactor to ORM
        
#         query = '''
#                     select sl.status_id, sl.description_group as status_group, sl.description_short as status_description, 
#                     ml.mineral_id, ml.mineral_name
#                     from (
#                     select distinct ms.status_id,
#                         case 
#                             when (ms.status_id >=2.0 and ms.status_id < 5.0) or (ms.status_id >=8.0 and ms.status_id < 9.0) 
#                             then mr.relation_id 
#                             else null
#                         end relation_id
#                     from mineral_status ms
#                     left join mineral_relation mr on ms.mineral_id = mr.mineral_id 
#                     where ms.mineral_id = %s
#                     and (mr.relation_type_id = 1 or null and mr.direct_relation = true or null)
#                     group by mr.relation_id, ms.status_id
#                     ) subquery
#                     inner join status_list sl 
#                     on sl.status_id = subquery.status_id
#                     left join mineral_log ml
#                     on ml.mineral_id = subquery.relation_id;
#             '''
#         queryset = StatusList.objects
#         return queryset.raw(query, [mineral_id])

#     def to_representation(self, instance):
#         raw_sql = self.get_status_description(instance.mineral_id)
#         query = list(raw_sql)
#         statuses = []
#         for status in query:
#             local = {}
#             local.update({
#                 # 'status_id': status.status_id,
#                 'group': status.status_group,
#                 'description': []
#             })
#             if status.mineral_id:
#                 relations = {
#                     'mineral_id': status.mineral_id,
#                     'mineral_name': status.mineral_name,
#                     }
#                 local['relations'] = [relations]
#             if len(statuses) > 0 and status.status_group not in set([loc_status['group'] for loc_status in statuses]):
#                 local['description'].append(status.status_description)
#                 statuses.append(local)
#             elif len(statuses) == 0:
#                 local['description'].append(status.status_description)
#                 statuses.append(local)
#             else:
#                 query_status = [loc_status for loc_status in statuses if loc_status['group'] == status.status_group][0]
#                 if status.status_description not in query_status['description']:
#                     query_status['description'].append(status.status_description)
#                 if relations:
#                     if 'relations' in query_status.keys() and status.mineral_id not in [relation['mineral_id'] for relation in query_status['relations']]:
#                         query_status['relations'].append(relations)
#                     else:
#                         query_status['relations'] = relations

#         return statuses

class MineralHierarchySerializer(serializers.BaseSerializer):

    @staticmethod
    def setup_eager_loading(queryset):
        # prefetch mineral_id and parent_id
        queryset = queryset.prefetch_related('mineral_id', 'parent_id', 'mineral_id__status')
        return queryset

    def get_hierarchy(self, mineral_id):
        query ='''
            with recursive hierarchy as (
                select
                    id,
                    mineral_id,
                    parent_id
                from
                    mineral_hierarchy
                where
                    mineral_id = %s
                union
                    select
                        e.id,
                        e.mineral_id,
                        e.parent_id
                    from
                        mineral_hierarchy e
                    inner join hierarchy h on h.parent_id = e.mineral_id
            ) select
                h.id, h.mineral_id, h.parent_id 
            from
                hierarchy h;
        '''
        queryset = self.setup_eager_loading(MineralHierarchy.objects)
        return queryset.raw(query, [mineral_id])

    def to_representation(self, instance):
        top_level = instance.mineral_id
        hierarchy = list(self.get_hierarchy(top_level))
        base_level = [mineral for mineral in hierarchy if mineral.parent_id is None]
        branches = len(set([mineral.mineral_id for mineral in base_level])) # unique values
        print(branches)

        # get the number of branches in hierarchy
        if branches > 0 and len(hierarchy) > 1:
            output = []
            for i in range(branches):
                output_inner = self.recursive_search(parent=base_level[i], top_level=top_level, hierarchy=hierarchy)
                # print(output_inner)
                output.append(*output_inner)
            return {
                'type': 'groups',
                'title': 'Groups Classification', 
                'data': output
            }
        else: 
            return None

    def recursive_search(self, parent, top_level, hierarchy):
        if not isinstance(parent, list):
            parent = [parent]
        output = []
        for index, parent in enumerate(parent):
            if parent.mineral_id.mineral_id == top_level:
                # breaks the recursion
                return []
            else:
                # continue the recursion
                children = [mineral for mineral in hierarchy if mineral.parent_id is not None and mineral.parent_id.mineral_id == parent.mineral_id.mineral_id]
                output.append({
                    'id': parent.id,
                    'mineral_name': parent.mineral_id.mineral_name, 
                    'mineral_id': parent.mineral_id.mineral_id, 
                    'formula': parent.mineral_id.mineral_formula_html(),
                    'ns_index': parent.mineral_id.get_ns_index(),
                    'status': StatusListSerializer(parent.mineral_id.status, many=True).data, 
                    'children': self.recursive_search(parent=children, top_level=top_level, hierarchy=hierarchy)  
                    })
        return output

class NickelStrunzSerializer(serializers.BaseSerializer):

    @staticmethod
    def setup_eager_loading(queryset):
        # select_related for 'to-one' relationships
        queryset = queryset.select_related('id_class', 'id_subclass', 'id_family')
        return queryset

    def to_representation(self, instance):
        output = []
        if instance.id_class is not None:
            ns_output = { 
                'type': 'ns',
                'title': 'Nickel-Strunz Classification', 
                'data': {} 
            }
            ns_output['data'].update({'ns_class': {
                    'index': instance.id_class.id_class,
                    'description': instance.id_class.description,
                }
            })
            if instance.id_subclass is not None:
                ns_output['data'].update({'ns_subclass': {
                        'index': instance.id_subclass.id_subclass,
                        'description': instance.id_subclass.description,
                    }
                })
            if instance.id_family is not None:
                ns_output['data'].update({'ns_family': {
                        'index': instance.id_family.id_family,
                        'description': instance.id_family.description,
                    }
                })
            output.append(ns_output)
            return ns_output
        else:
            return None

class MineralClassificationSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        output = []
        # Groups classification part
        ns = NickelStrunzSerializer(instance).data
        groups = MineralHierarchySerializer(instance).data
        output = [ns, groups]
        output = [classification for classification in output if classification is not None]

        if len(output) > 0:
            return output
        else:
            return None

class MineralCountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = MineralCountry

    @staticmethod
    def setup_eager_loading(queryset):
        # select_related for 'to-one' relationships
        queryset = queryset.select_related('country_id')
        return queryset

    def to_representation(self, instance):
        return {
            'country_name': instance.country_id.country_name,
            'country_id': instance.country_id.country_id,
            'country_iso': instance.country_id.alpha_3,
            'country_region': instance.country_id.region,
            'note': instance.note
        }


class MineralHistorySerializer(serializers.ModelSerializer):
    discovery_year = serializers.ReadOnlyField(source='get_discovery_year')
    discovery_year_note = serializers.CharField(read_only=True)
    first_usage_date = serializers.CharField(read_only=True)
    first_known_use = serializers.CharField(read_only=True)

    class Meta:
        model = MineralHistory
        fields = ['discovery_year', 'discovery_year_note', 'first_usage_date', 'first_known_use']

class MineralRelationSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        print(instance)
        objects = instance.filter(related_relations__relation_type_id=1).order_by('mineral_name') \
                                            .select_related('id_class', 'id_subclass', 'id_family') \
                                            .prefetch_related('status')
        if len(objects) > 0:
            output = []
            for object in objects:
                output.append({ 
                    'mineral_id': object.mineral_id, 
                    'mineral_name': object.mineral_name, 
                    'formula': object.mineral_formula_html(),
                    'ns_index': object.get_ns_index(),
                    'status': StatusListSerializer(object.status, many=True).data 
                    }) 
        else:
            output = None
        return output


class MineralBaseSerializer(serializers.ModelSerializer):
    mineral_id = serializers.UUIDField(read_only=True)
    mineral_name = serializers.CharField(required=True)
    formula = serializers.ReadOnlyField(source='mineral_formula_html')
    statuses = StatusDescriptionSerializer(source="mineral_status")
    # statuses = serializers.SerializerMethodField()
    note = serializers.CharField()
    ns_index = serializers.ReadOnlyField(source='get_ns_index')
    history = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at =serializers.DateTimeField(read_only=True)

    class Meta:
        model = MineralLog
        fields = ['mineral_id', 'mineral_name', 'formula', 'statuses', 'note', 
                  'ns_index', 'history', 'created_at', 'updated_at',]

    def get_discovery_country(self, instance):
        queryset = instance.country_mineral
        resp = MineralCountrySerializer.setup_eager_loading(queryset)
        serializer = MineralCountrySerializer(resp, many=True)
        return serializer.data

    def get_history(self, instance):
        output = {}
        if hasattr(instance, 'history'):
            history_queryset = MineralHistorySerializer(instance.history).data
            output.update(history_queryset)
        country_queryset = self.get_discovery_country(instance)
        if len(country_queryset):
                output.update({ 'discovery_country': country_queryset })
        if output:
            return output

    def get_classification(self, instance):
        return MineralClassificationSerializer(instance).data

    def get_statuses(self, instance):
        return StatusDescriptionSerializer(instance).data


class MineralDetailSerializer(MineralBaseSerializer, serializers.ModelSerializer):
    tabs = serializers.SerializerMethodField()

    class Meta:
        model = MineralLog
        fields = MineralBaseSerializer.Meta.fields + ['tabs']

    def get_tabs(self, instance):
        tabs = NuxtTabsSerializer(instance).data
        return tabs if len(tabs) else None

class MineralChildrenSerializer(serializers.BaseSerializer):

    @staticmethod
    def setup_eager_loading(queryset):
        # prefetch mineral_id and parent_id
        queryset = queryset.select_related('mineral_id', 'parent_id')
        queryset = queryset.prefetch_related('mineral_id__status', 'mineral_id__id_class', 'mineral_id__id_subclass', 'mineral_id__id_family')
        return queryset

    def to_representation(self, instance):
        hierarchy = instance.annotate(status_min=Min('mineral_id__status__status_id'),
                                        is_bottom_level=Case(When(Q(mineral_id__status__status_id__gte=1.0) & Q(mineral_id__status__status_id__lt=2.0), then=False), default=True, output_field=BooleanField()))\
                                .order_by('is_bottom_level','status_min')

        if len(hierarchy) > 0:
            output = []
            for mineral in hierarchy:
                mineral_dict = {
                    'id': mineral.id,
                    'mineral_id': mineral.mineral_id.mineral_id,
                    'mineral_name': mineral.mineral_id.mineral_name,
                    'formula': mineral.mineral_id.mineral_formula_html(),
                    'ns_index': mineral.mineral_id.get_ns_index(),
                    'status': StatusListSerializer(mineral.mineral_id.status, many=True).data 
                }
                if not mineral.is_bottom_level:
                    mineral_dict['children'] = []
                output.append(mineral_dict)
            return output
        else:
            return None


# per mineral serializers

class MineralHistoryNodeSerializer(serializers.BaseSerializer):

    @staticmethod
    def setup_eager_loading(queryset):
        # prefetch mineral_id and parent_id
        queryset = queryset.select_related('history')
        # queryset = queryset.prefetch_related('discovery_country')
        return queryset

    def to_representation(self, instance):
        history = self.get_history(instance)
        return {
            'history': history
        }

    def get_related_discovery_countries(self):
        # a function which grabs discovery countries of all minerals, groups and count the results
        queryset = MineralCountry.objects.all()
        resp = discovery_country_counts(queryset)
        serializer = discoveryCountryCountsSerializer(resp, many=True)
        return serializer.data
        
    def get_discovery_country(self, obj):
        # a function which firstly joins country_list to mineral_country and then outputs the data
        queryset = obj.country_mineral
        resp = MineralCountrySerializer.setup_eager_loading(queryset)
        serializer = MineralCountrySerializer(resp, many=True)
        return serializer.data

    def get_history(self, obj):
        # a function which collects history and discovery_country data and merges it
        output = {}
        if hasattr(obj, 'history'):
            history_queryset = MineralHistorySerializer(obj.history).data
            output.update(history_queryset)
        country_queryset = self.get_discovery_country(obj)
        if len(country_queryset) > 0:
                output.update({ 'discovery_country': country_queryset })

        relations = []
        country_counts = self.get_related_discovery_countries()
        output.update({ 'discovery_country_counts': country_counts })
        return output

class NuxtTabsSerializer(serializers.BaseSerializer):

    def get_tabs(self, mineral_id):
        query = '''
            select nt.tab_id, nt.tab_short_name, nt.tab_long_name from nuxt_tabs nt 
            where nt.tab_short_name in ( 
            select 'history' 
            where exists (select 1 from mineral_history mh where mh.mineral_id = %(mineral_id)s) or
            exists (select 1 from mineral_log ml where ml.mineral_id = %(mineral_id)s) 
            union 
            select 'classification' 
            where exists (select 1 from mineral_hierarchy mh 
                            where mh.mineral_id = %(mineral_id)s 
                            or mh.parent_id = %(mineral_id)s) or 
            exists (select 1 from mineral_log ml where ml.mineral_id = %(mineral_id)s and ml.id_class is not null) 
            union 
            select 'relations' 
            where exists (select 1 from mineral_relation mr where mr.mineral_id = %(mineral_id)s)
            );
        '''
        queryset = NuxtTabs.objects.all()
        return queryset.raw(query, { 'mineral_id': mineral_id })

    def to_representation(self, instance):
        mineral_id = instance.mineral_id
        tabs = list(self.get_tabs(mineral_id))
        output = []
        for tab in tabs:
            output.append({ 'tab_id': tab.tab_id, 'tab_short_name': tab.tab_short_name, 'tab_long_name': tab.tab_long_name })
        return output
