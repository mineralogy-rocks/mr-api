# -*- coding: UTF-8 -*-
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from rest_framework import serializers

from ..models.core import Country
from ..models.core import Status
from ..models.crystal import CrystalSystem
from ..models.mineral import Mineral
from ..models.mineral import MineralFormula
from ..models.mineral import MineralHierarchy
from ..models.mineral import MineralHistory
from ..models.mineral import MineralIonPosition
from .core import CountryListSerializer
from .core import FormulaSourceSerializer
from .core import StatusListSerializer
from .crystal import CrystalSystemSerializer
from .ion import MineralIonPositionSerializer


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


class HierarchyParentHyperlinkSerializer(serializers.ModelSerializer):

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


class MineralListSerializer_(serializers.ModelSerializer):

    url = serializers.URLField(source="get_absolute_url")
    ns_index = serializers.CharField(source="ns_index_")
    updated_at = serializers.SerializerMethodField()
    formulas = MineralFormulaSerializer(many=True)
    description = serializers.CharField(source="short_description")
    is_grouping = serializers.BooleanField()
    seen = serializers.IntegerField()

    hierarchy = serializers.JSONField(source="hierarchy_")
    ions = serializers.JSONField(source="ions_")
    crystal_systems = serializers.JSONField(source="crystal_systems_")
    statuses = serializers.JSONField(source="statuses_")
    relations = serializers.JSONField(source="relations_")
    discovery_countries = serializers.JSONField(source="discovery_countries_")
    history = serializers.JSONField(source="history_")

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "ima_symbol",
            "url",
            "ns_index",
            "updated_at",
            "formulas",
            "description",
            "is_grouping",
            "seen",
            "hierarchy",
            "ions",
            "crystal_systems",
            "statuses",
            "relations",
            "discovery_countries",
            "history",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = []

        prefetch_related = [
            models.Prefetch("formulas", MineralFormula.objects.filter(show_on_site=True).select_related("source")),
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset

    def get_updated_at(self, instance):
        return naturalday(instance.updated_at)

    def get_ions(self, instance):
        output = MineralIonPositionSerializer(instance.positions, many=True).data

        output_ = []
        positions_ = []

        for ion in output:
            position_ = ion["position"]
            if position_["id"] not in positions_:
                positions_.append(position_["id"])
                output_.append(
                    {
                        "position": position_,
                        "ions": [ion_["ion"] for ion_ in output if ion_["position"]["id"] == position_["id"]],
                    }
                )

        return output_

    def get_crystal_systems(self, instance):
        if instance.is_grouping:
            # crystal_systems = MineralCrystallography.objects.all().values('crystal_system') \
            #                                                       .filter(Q(mineral__parents_hierarchy__parent=instance.id)) \
            #                                                       .annotate(
            #                                                         id=F('crystal_system__id'),
            #                                                         name=F('crystal_system__name'),
            #                                                         counts=Count('mineral', distinct=True)
            #                                                       )
            crystal_systems = (
                instance.children_hierarchy.select_related("mineral")
                .values("mineral__crystal_systems")
                .annotate(
                    id=F("mineral__crystal_systems__id"),
                    name=F("mineral__crystal_systems__name"),
                    counts=Count("mineral", distinct=True),
                )
            )
            # crystal_systems = MineralHierarchy.objects.values('mineral__crystal_systems') \
            #                                     .filter(parent=instance.id) \
            #                                     .annotate(
            #                                         id=F('mineral__crystal_systems__id'),
            #                                         name=F('mineral__crystal_systems__name'),
            #                                         counts=Count('mineral', distinct=True)
            #                                     )

            return crystal_systems.values("id", "name", "counts")
        return CrystalSystemSerializer(instance.crystal_systems, many=True).data


class MineralLinkSerializer(serializers.Serializer):

    mindat = serializers.URLField(source="get_mindat_url")
    rruff = serializers.URLField(source="get_rruff_url")

    class Meta:
        model = Mineral
        fields = [
            "mindat",
            "rruff",
        ]


class MineralListSerializer(serializers.ModelSerializer):

    url = serializers.URLField(source="get_absolute_url")
    ns_index = serializers.CharField(source="ns_index_")
    description = serializers.CharField()  # source="short_description"
    is_grouping = serializers.BooleanField()
    seen = serializers.IntegerField()
    updated_at = serializers.SerializerMethodField()

    formulas = MineralFormulaSerializer(many=True)
    hierarchy = serializers.SerializerMethodField()
    crystal_systems = serializers.SerializerMethodField()
    statuses = StatusListSerializer(many=True)
    relations = serializers.JSONField(source="relations_")
    discovery_countries = serializers.SerializerMethodField()
    history = MineralHistorySerializer()
    links = MineralLinkSerializer(source="*")

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "url",
            "ns_index",
            "ima_symbol",
            "description",
            "is_grouping",
            "seen",
            "updated_at",
            "formulas",
            "hierarchy",
            "crystal_systems",
            "statuses",
            "relations",
            "discovery_countries",
            "history",
            "links",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = [
            "history",
        ]

        prefetch_related = [
            "crystal_systems",
            models.Prefetch("formulas", MineralFormula.objects.select_related("source")),
            models.Prefetch(
                "children_hierarchy",
                MineralHierarchy.objects.select_related("mineral", "parent").order_by("mineral__statuses__status_id"),
            ),
            models.Prefetch(
                "parents_hierarchy",
                MineralHierarchy.objects.select_related("mineral", "parent").order_by("parent__statuses__status_id"),
            ),
            models.Prefetch(
                "discovery_countries",
                Country.objects.filter(~Q(id=250)),
            ),
            models.Prefetch("statuses", Status.objects.select_related("group")),
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset

    def get_updated_at(self, instance):
        return naturalday(instance.updated_at)

    def get_crystal_systems(self, instance):
        if instance.is_grouping:
            return instance.crystal_systems_
        return CrystalSystemSerializer(instance.crystal_systems, many=True).data

    def get_discovery_countries(self, instance):
        if instance.is_grouping:
            return instance.discovery_countries_
        return CountryListSerializer(instance.discovery_countries, many=True).data

    def get_hierarchy(self, instance):
        if instance.is_grouping:
            return HierarchyChildrenHyperlinkSerializer(
                instance.children_hierarchy.all()[:5], context=self.context, many=True
            ).data
        return HierarchyParentHyperlinkSerializer(
            instance.parents_hierarchy.all()[:5], context=self.context, many=True
        ).data
