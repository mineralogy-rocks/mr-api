# -*- coding: UTF-8 -*-
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.db.models import Q, F, OuterRef, Subquery
from django.db.models import Prefetch
from rest_framework import serializers

from ..models.core import Status
from ..models.crystal import CrystalSystem
from ..models.mineral import Mineral
from ..models.mineral import MineralFormula
from ..models.mineral import MineralHierarchy
from ..models.mineral import MineralHistory
from ..models.mineral import MineralIonPosition
from ..models.mineral import MineralRecursiveRelationView
from .core import CountryListSerializer
from .core import FormulaSourceSerializer
from ..utils import formula_to_html


class MineralHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MineralHistory
        fields = [
            "id",
            "discovery_year",
            "ima_year",
            "publication_year",
            "approval_year",
            "discovery_year_note",
            "first_usage_date",
            "first_known_use",
        ]


class HierarchyParentsHyperlinkSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(source="parent", read_only=True)

    name = serializers.StringRelatedField(source="parent")
    url = serializers.HyperlinkedRelatedField(source="parent", read_only=True, view_name="core:mineral-detail")

    class Meta:
        model = MineralHierarchy
        fields = [
            "id",
            "name",
            "url",
        ]


class HierarchyChildrenHyperlinkSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(source="mineral", read_only=True)

    name = serializers.StringRelatedField(source="mineral")
    url = serializers.HyperlinkedRelatedField(source="mineral", read_only=True, view_name="core:mineral-detail")

    class Meta:
        model = MineralHierarchy
        fields = [
            "id",
            "name",
            "url",
        ]


class MineralFormulaSerializer(serializers.ModelSerializer):

    formula = serializers.CharField(source="formula_escape")
    source = FormulaSourceSerializer()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = MineralFormula
        fields = [
            "formula",
            "note",
            "source",
            "show_on_site",
            "created_at",
        ]

    def get_created_at(self, instance):
        return naturalday(instance.created_at)


class MineralFormulaRelatedSerializer(MineralFormulaSerializer):

    mineral = serializers.PrimaryKeyRelatedField(read_only=True)
    from_ = serializers.JSONField(source="from")

    class Meta:
        model = MineralFormula
        fields = MineralFormulaSerializer.Meta.fields + ["mineral", "from_",]


class MineralRetrieveSerializer(serializers.ModelSerializer):

    ns_index = serializers.CharField(source="ns_index_")
    formula = serializers.CharField(source="formula_html")
    is_grouping = serializers.BooleanField()
    seen = serializers.IntegerField()

    hierarchy = serializers.SerializerMethodField()
    # hierarchy = HierarchyChildrenHyperlinkSerializer(source='children_hierarchy', many=True)

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "ns_index",
            "formula",
            "is_grouping",
            "seen",
            "hierarchy",
            # 'ions',
            # 'crystal_systems',
            # 'colors',
            # 'statuses',
            # 'relations',
            # 'discovery_countries',
            # 'history',
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = [
            "history",
        ]

        prefetch_related = [
            models.Prefetch("statuses", Status.objects.select_related("group")),
            models.Prefetch("crystal_systems", CrystalSystem.objects.all().distinct()),
            # models.Prefetch('crystal_systems', CrystalSystem.objects.filter(Q(minerals__mineral__parents_hierarchy__parent__in=queryset.values('id'))),
            #                 to_attr='crystal_system_counts'
            #                 ),
            # models.Prefetch('crystallography', MineralCrystallography.objects.filter(Q(mineral__parents_hierarchy__parent__in=queryset.values('id')) |
            #                                                                          Q(mineral__in=queryset.values('id'))) \
            #                                                                  .select_related('crystal_system') \
            #                                                                  .defer('crystal_class', 'space_group', 'a', 'b', 'c', 'alpha', 'gamma', 'z'),
            #                                                                  to_attr='crystal_system_counts'
            #                                                                  ),
            models.Prefetch(
                "parents_hierarchy",
                MineralHierarchy.objects.select_related("parent", "mineral"),
            ),
            models.Prefetch(
                "ions",
                MineralIonPosition.objects.select_related("ion", "position").order_by("position", "ion__formula"),
                to_attr="positions",
            ),
            "discovery_countries",
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset

    def get_hierarchy(self, instance):
        if instance.is_grouping:
            return HierarchyChildrenHyperlinkSerializer(
                instance.children_hierarchy, context=self.context, many=True
            ).data
        return HierarchyParentsHyperlinkSerializer(instance.parents_hierarchy, context=self.context, many=True).data


class MineralListSerializer(serializers.ModelSerializer):
    '''
    The main serializer for the mineral list view. It serializes the
    data from raw sql query; therefore, it doesn't support prefetching.
    MineralListSecondarySerializer allows injecting prefetched data into this serializer.
    '''
    ns_index = serializers.CharField(source="ns_index_")
    description = serializers.CharField(source="short_description")
    is_grouping = serializers.BooleanField()
    seen = serializers.IntegerField()
    updated_at = serializers.SerializerMethodField()

    crystal_systems = serializers.JSONField()
    statuses = serializers.JSONField(source='_statuses')
    relations = serializers.JSONField(source="_relations")
    discovery_countries = serializers.JSONField(source="_discovery_countries")
    history = serializers.JSONField(source="_history")
    links = serializers.SerializerMethodField()
    ordering = serializers.SerializerMethodField()

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "slug",
            "mindat_id",
            "ns_index",
            "ima_symbol",
            "description",
            "is_grouping",
            "seen",
            "updated_at",
            "crystal_systems",
            "statuses",
            "relations",
            "discovery_countries",
            "history",
            "links",
            "ordering",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = [
        ]

        prefetch_related = [
            # models.Prefetch("formulas", MineralFormula.objects.select_related("source")),
            # models.Prefetch(
            #     "children_hierarchy",
            #     MineralHierarchy.objects.select_related("mineral", "parent").order_by("mineral__statuses__status_id"),
            # ),
            # models.Prefetch(
            #     "parents_hierarchy",
            #     MineralHierarchy.objects.select_related("mineral", "parent").order_by("parent__statuses__status_id"),
            # ),
            # models.Prefetch(
            #     "discovery_countries",
            #     Country.objects.filter(~Q(id=250)),
            # ),
            # models.Prefetch("statuses", Status.objects.select_related("group")),
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset

    def get_updated_at(self, instance):
        return naturalday(instance.updated_at)

    def get_discovery_countries(self, instance):
        if instance.is_grouping:
            return instance.discovery_countries_
        return CountryListSerializer(instance.discovery_countries, many=True).data

    def get_links(self, instance):
        links = [
            {
                "name": "RRUFF",
                "display_name": "rruff.info",
                "link": instance.get_rruff_url(),
            },
            {
                "name": "COD",
                "display_name": "Open Crystallography Database",
                "link": instance.get_cod_url(),
            },
            {
                "name": "AMCSD",
                "display_name": "American Mineralogist Crystal Structure Database",
                "link": instance.get_amcsd_url(),
            }
        ]
        mindat_link = instance.get_mindat_url()
        if mindat_link:
            links.append(
                {
                    "name": "Mindat",
                    "display_name": "mindat.org",
                    "link": mindat_link,
                }
            )

        return links

    def get_ordering(self, instance):
        return hasattr(instance, "ordering") and instance.ordering or None


class MineralListSecondarySerializer(serializers.ModelSerializer):
    '''
    We're using this serializer for injecting additional data into the
    main serializer of the list view
    '''
    formulas = MineralFormulaSerializer(many=True)

    class Meta:
        model = Mineral
        fields = [
            "id",
            "formulas",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = [
        ]

        prefetch_related = [
            models.Prefetch("formulas", MineralFormula.objects.select_related("source")),
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


class BaseMineralRelationsSerializer(serializers.Serializer):

    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    formula = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "name",
            "slug",
            "formula",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset, request = kwargs.get("queryset"), kwargs.get("request")

        select_related = [
        ]
        prefetch_related = [
            Prefetch("formulas", MineralFormula.objects.select_related("source").filter(source=1), to_attr="_formulas"),
        ]
        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)

        return queryset

    def get_formula(self, instance):
        return formula_to_html(instance._formulas[0].formula) if instance._formulas else None



class MineralRelationsSerializer(BaseMineralRelationsSerializer):

    id = serializers.IntegerField()

    class Meta:
        fields = BaseMineralRelationsSerializer.Meta.fields

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset, request = kwargs.get("queryset"), kwargs.get("request")

        select_related = [
        ]
        prefetch_related = [
            Prefetch("relation__formulas", MineralFormula.objects.select_related("source").filter(source=1), to_attr="_formulas"),
        ]
        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)

        return queryset

    def get_formula(self, instance):
        return formula_to_html(instance.relation._formulas[0].formula) if instance.relation._formulas else None
