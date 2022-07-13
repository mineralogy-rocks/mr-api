# -*- coding: UTF-8 -*-
from django.db.models import Case
from django.db.models import CharField
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat
from django.db.models.functions import Right
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import GenericViewSet

from .filters import MineralFilter
from .filters import StatusFilter
from .models.core import NsClass
from .models.core import Status
from .models.mineral import Mineral
from .models.mineral import MineralStatus
from .pagination import CustomLimitOffsetPagination
from .serializers.base import BaseSerializer
from .serializers.core import StatusListSerializer
from .serializers.mineral import MineralListSerializer
from .serializers.mineral import MineralRetrieveSerializer


class StatusViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):

    http_method_names = [
        "get",
        "options",
        "head",
    ]

    queryset = Status.objects.all()
    serializer_class = StatusListSerializer

    renderer_classes = [
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    permission_classes = [
        AllowAny,
    ]
    authentication_classes = []

    ordering_fields = [
        "status_id",
        "status_group",
    ]
    ordering = [
        "status_id",
    ]

    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "description_short",
        "description_long",
        "status_group__name",
    ]
    filterset_class = StatusFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, "setup_eager_loading"):
            queryset = serializer_class.setup_eager_loading(
                queryset=queryset, request=self.request
            )

        return queryset


class NickelStrunzViewSet(ListModelMixin, GenericViewSet):

    http_method_names = [
        "get",
        "options",
        "head",
    ]

    queryset = []
    serializer_class = BaseSerializer

    renderer_classes = [
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    permission_classes = [
        AllowAny,
    ]
    authentication_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["classes"]:
            queryset = NsClass.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = [
            {
                "id": 0,
                "name": "Nickel-Strunz Classes",
                "url": reverse("core:nickel-strunz-classes", request=self.request),
            },
            {
                "id": 1,
                "name": "Nickel-Strunz Subclasses",
                "url": reverse("core:status-list", request=self.request),
            },
        ]

        return Response(queryset, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False, url_path="classes")
    def classes(self, request, *args, **kwargs):
        return Response({"some": "asfsa"}, status=status.HTTP_200_OK)


class MineralViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):

    http_method_names = [
        "get",
        "options",
        "head",
    ]

    queryset = Mineral.objects.all()
    serializer_class = MineralListSerializer

    renderer_classes = [
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    pagination_class = CustomLimitOffsetPagination

    permission_classes = [
        AllowAny,
    ]
    authentication_classes = []

    ordering_fields = [
        "name",
    ]
    ordering = [
        "name",
    ]

    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = MineralFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, "setup_eager_loading"):
            queryset = serializer_class.setup_eager_loading(
                queryset=queryset, request=self.request
            )

        # isostructural_minerals_ = NsFamily.objects.values('ns_family') \
        #                                           .annotate(count=Count('minerals')) \
        #                                           .filter(ns_family=OuterRef('ns_family'))

        # relations_count_ = MineralRelation.objects.values('relation') \
        #                                           .filter(Q(direct_relation=True)) \
        #                                           .annotate(
        #                                              varieties_count=Case(
        #                                                  When(status__status__status_group__name='varieties', then=Count('relation')),
        #                                                  default=Value(None)
        #                                              ),
        #                                              polytypes_count=Case(
        #                                                 When(status__status__status_group__name='polytypes', then=Count('relation')),
        #                                                 default=Value(None)
        #                                              )
        #                                           ) \
        #                                           .filter(mineral=OuterRef('id'))

        # history_ = MineralHierarchy.objects.values('parent') \
        #                                    .filter(Q(parent=OuterRef('id'))) \
        #                                    .annotate(
        #                                      discovery_year_min=Min('mineral__history__discovery_year_min'),
        #                                      discovery_year_max=Max('mineral__history__discovery_year_max')
        #                                    )

        # ions_ = MineralIonPosition.objects.all().values('position') \
        #                                         .filter(Q(mineral=OuterRef('id'))) \
        #                                         .annotate(
        #                                             ions_= JSONObject(
        #                                                 id=F('position__id'),
        #                                                 name=F('position__name'),
        #                                                 ions=ArrayAgg('ion__formula')
        #                                             )
        #                                         ).order_by('position__name')

        # crystal_systems_ = MineralCrystallography.objects.all().values('crystal_system') \
        #                                                        .filter(Q(mineral__parents_hierarchy__parent=OuterRef('id'))) \
        #                                                        .annotate(
        #                                                            crystal_systems_=JSONObject(
        #                                                                 id=F('crystal_system__id'),
        #                                                                 name=F('crystal_system__name'),
        #                                                                 count=Count('mineral', distinct=True)
        #                                                            )
        #                                                        )

        is_grouping_ = MineralStatus.objects.filter(
            Q(mineral=OuterRef("id")) & Q(status__status_group=1)
        )

        queryset = queryset.annotate(
            is_grouping=Exists(is_grouping_),
            ns_index_=Case(
                When(
                    ns_class__isnull=False,
                    then=Concat(
                        "ns_class__id",
                        Value("."),
                        Coalesce(Right("ns_subclass__ns_subclass", 1), Value("0")),
                        Coalesce(Right("ns_family__ns_family", 1), Value("0")),
                        Value("."),
                        Coalesce("ns_mineral", Value("0")),
                        output_field=CharField(),
                    ),
                ),
                default=None,
            ),
        )

        # queryset = queryset.annotate(
        #                         ions_=Case(
        #                             When(is_grouping=True, then=ArraySubquery(ions_.values('ions_'))),
        #                             default=[]
        #                         ),
        #                         crystal_systems_=ArraySubquery(crystal_systems_.values('crystal_systems_')),
        #                         relations_=JSONObject(
        #                             isostructural_minerals=Subquery(isostructural_minerals_.values('count')),
        #                             varieties=Subquery(relations_count_.values('varieties_count')),
        #                             polytypes=Subquery(relations_count_.values('polytypes_count')),
        #                         ),
        #                         history_=JSONObject(
        #                             discovery_year_min=Case(
        #                                 When(is_grouping=True, then=Subquery(history_.values('discovery_year_min'))),
        #                                 default=F('history__discovery_year_min')
        #                             ),
        #                             discovery_year_max=Case(
        #                                 When(is_grouping=True, then=Subquery(history_.values('discovery_year_max'))),
        #                                 default=F('history__discovery_year_max')
        #                             ),
        #                         )
        #                     )

        queryset = queryset.defer(
            "ns_class",
            "ns_subclass",
            "ns_mineral",
            "note",
            "created_at",
            "updated_at",
            "history__mineral_id",
            "history__discovery_year_note",
            "history__certain",
            "history__first_usage_date",
            "history__first_known_use",
        )

        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if "q" in self.request.query_params:
            query = self.request.query_params.get("q", "")
            queryset = queryset.filter(name__unaccent__trigram_word_similar=query)

        discovery_countries = self.request.query_params.get("discovery_countries")

        if self.request.query_params.get("filter_related", False) == "true":
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

    def get_serializer_class(self):

        if self.action in ["list"]:
            return MineralListSerializer
        elif self.action in ["retrieve"]:
            return MineralRetrieveSerializer

        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        results = []

        if page:
            sql, params = page.query.sql_with_params()

            results = Mineral.objects.raw(
                """
                SELECT ml.*,
                CASE
                WHEN ml.is_grouping
                THEN (
                        SELECT COALESCE(json_agg(
                            JSONB_BUILD_OBJECT('id', ml_.id, 'name', ml_.name, 'url', concat('/mineral/', ml_.id)
                        )  ORDER BY sl.status_id), '[]'::json)
                        FROM mineral_hierarchy mh
                        INNER JOIN mineral_log ml_ ON mh.mineral_id = ml_.id
                        INNER JOIN mineral_status ms ON mh.mineral_id = ms.mineral_id
                        INNER JOIN status_list sl ON ms.status_id = sl.id
                        WHERE mh.parent_id = ml.id
                    )
                ELSE (
                        SELECT COALESCE(json_agg(
                            JSONB_BUILD_OBJECT('id', ml_.id, 'name', ml_.name, 'url', concat('/mineral/', ml_.id)
                            )  ORDER BY sl.status_id), '[]'::json)
                        FROM mineral_hierarchy mh
                        INNER JOIN mineral_log ml_ ON mh.parent_id = ml_.id
                        INNER JOIN mineral_status ms ON mh.parent_id  = ms.mineral_id
                        INNER JOIN status_list sl ON ms.status_id = sl.id
                        WHERE mh.mineral_id = ml.id
                    )
                END AS hierarchy_,

                CASE
                    WHEN ml.is_grouping
                    THEN
                        (
                            SELECT COALESCE(json_agg(temp_), '[]'::json)
                            FROM (
                                    WITH RECURSIVE hierarchy as (
                                        SELECT
                                            id,
                                            mineral_id,
                                            parent_id
                                        FROM mineral_hierarchy
                                        WHERE mineral_id = ml.id
                                        UNION
                                        SELECT
                                            e.id,
                                            e.mineral_id,
                                            e.parent_id
                                        FROM mineral_hierarchy e
                                        INNER JOIN hierarchy h ON h.mineral_id = e.parent_id
                                    )
                                    SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id,
                                            count(h.mineral_id) AS counts,
                                            to_jsonb(sgl) AS status_group
                                    FROM hierarchy h
                                    INNER JOIN mineral_status ms ON ms.mineral_id = h.mineral_id
                                    INNER JOIN status_list sl ON sl.id = ms.status_id
                                    INNER JOIN status_group_list sgl ON sgl.id = sl.status_group_id
                                    WHERE h.parent_id IS NOT NULL AND sgl.id IN (3, 4, 11)
                                    GROUP BY sgl.id
                            ) temp_
                        )
                    ELSE
                        (
                            SELECT COALESCE(json_agg(temp_), '[]'::json)
                            FROM (
                                SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id, counts, status_group FROM (
                                    SELECT COUNT(mr.mineral_id) AS counts, to_jsonb(sgl) AS status_group
                                    FROM mineral_relation mr
                                    INNER JOIN mineral_status ms ON mr.mineral_status_id = ms.id
                                    INNER JOIN status_list sl ON ms.status_id = sl.id
                                    INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
                                    WHERE mr.direct_relation AND
                                        mr.mineral_id = ml.id AND
                                        mr.relation_type_id = 1 AND
                                        sgl.id  IN (1, 4)
                                    GROUP BY sgl.id
                                    UNION
                                    SELECT count(ml_.id) AS counts, (SELECT to_jsonb(sgl) AS status_group FROM status_group_list sgl WHERE sgl.id = 11)
                                    FROM ns_family nf
                                    INNER  JOIN mineral_log ml_ ON nf.id = ml_.ns_family
                                    INNER JOIN mineral_status ms ON ms.mineral_id = ml_.id
                                    INNER JOIN status_list sl ON ms.status_id = sl.id
                                    INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
                                    WHERE sgl.id = 11 and nf.id = ml.ns_family and ml_.id <> ml.id
                                    HAVING count(ml_.id) > 0
                                ) inner_
                            ) temp_
                        )
                END AS relations_,

                (
                    SELECT COALESCE(json_agg(
                        JSONB_BUILD_OBJECT(
                            'id', sl.status_id,
                            'description_short', sl.description_short,
                            'description_long', sl.description_long
                        ) ORDER BY sl.status_id), '[]'::json ) AS statuses_
                    FROM mineral_status ms
                    INNER JOIN status_list sl ON ms.status_id = sl.id
                    WHERE ms.mineral_id = ml.id
                ),

                CASE
                    WHEN ml.is_grouping
                    THEN
                        (
                            SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                                SELECT cl.id, cl.name, cl.alpha_2 AS iso_code, count(cl.id) AS counts
                                FROM mineral_country mc
                                INNER JOIN country_list cl ON mc.country_id = cl.id
                                INNER JOIN mineral_hierarchy mh ON mh.mineral_id = mc.mineral_id
                                WHERE mh.parent_id = ml.id
                                AND cl.id <> 250
                                GROUP BY cl.id
                                ORDER BY counts DESC
                            ) temp_
                        )
                    ELSE
                        (
                            SELECT COALESCE(json_agg(
                                JSONB_BUILD_OBJECT(
                                    'id', cl.id,
                                    'name', cl.name,
                                    'iso_code', cl.alpha_2
                                ) ORDER BY cl.id), '[]'::json ) AS discovery_countries_
                            FROM mineral_country mc
                            INNER JOIN country_list cl ON mc.country_id = cl.id
                            WHERE mc.mineral_id = ml.id
                        )
                    END AS discovery_countries_,

                CASE
                    WHEN ml.is_grouping
                    THEN
                        (
                            SELECT COALESCE(json_agg(temp_), '[]'::json)
                            FROM (
                                SELECT cl.id, cl.name, cl.code, COUNT(cl.id) AS counts
                                FROM mineral_color mc
                                INNER JOIN color_list cl ON mc.color_id = cl.id
                                INNER JOIN mineral_hierarchy mh ON mh.mineral_id = mc.mineral_id
                                WHERE mh.parent_id  = ml.id
                                GROUP BY cl.id
                                ORDER BY counts DESC
                            ) temp_
                        )
                    ELSE
                        (
                           SELECT COALESCE(json_agg(temp_), '[]'::json)
                           FROM (
                                SELECT cl.id, cl.name, cl.code, COUNT(cl.id) AS counts
                                FROM mineral_color mc
                                INNER JOIN color_list cl ON mc.color_id = cl.id
                                WHERE mc.mineral_id  = ml.id
                                GROUP BY cl.id
                                ORDER BY id
                            ) temp_
                        )
                END AS colors_,

                CASE
                    WHEN ml.is_grouping
                    THEN
                        (
                            SELECT COALESCE(json_agg(temp_), '[]'::json)
                            FROM (
                                SELECT csl.id, csl.name, COUNT(DISTINCT mh.mineral_id) AS counts
                                FROM mineral_crystallography mc
                                INNER JOIN crystal_system_list csl ON mc.crystal_system_id = csl.id
                                INNER JOIN mineral_hierarchy mh ON mh.mineral_id = mc.mineral_id
                                WHERE mh.parent_id  = ml.id
                                GROUP BY csl.id
                                ORDER BY csl.id
                            ) temp_
                        )
                    ELSE
                        (
                            SELECT COALESCE(json_agg(temp_), '[]'::json)
                            FROM (
                                SELECT csl.id, csl.name, COUNT(DISTINCT mc.mineral_id) AS counts
                                FROM mineral_crystallography mc
                                INNER JOIN crystal_system_list csl ON mc.crystal_system_id = csl.id
                                WHERE mc.mineral_id  = ml.id
                                GROUP BY csl.id
                                ORDER BY csl.id
                            ) temp_
                        )
                END AS crystal_systems_,

                (
                    SELECT COALESCE(json_agg(temp_), '[]'::json) AS ions_
                    FROM (
                        SELECT mip.ion_position_id AS id, iol.name AS name,
                        array_agg(
                                    JSONB_BUILD_OBJECT('id', io.id, 'name', io.name, 'formula', io.formula)
                                    ORDER BY io.id DESC
                                )  AS ions
                        FROM mineral_ion_position mip
                        INNER JOIN ion_position_list iol ON (mip.ion_position_id = iol.id)
                        INNER JOIN ion_log io ON (mip.ion_id = io.id)
                        WHERE mip.mineral_id = ml.id
                        GROUP BY mip.ion_position_id, iol.name
                        ORDER BY mip.ion_position_id
                    ) temp_
                ),

                CASE
                    WHEN ml.is_grouping
                    THEN (
                            SELECT to_json(temp_) AS history_ FROM (
                                SELECT min(mhis.discovery_year_min) AS discovery_year_min, max(mhis.discovery_year_max) AS discovery_year_max
                                FROM mineral_hierarchy mh
                                INNER JOIN mineral_log ml_ ON mh.mineral_id = ml_.id AND mh.parent_id = ml.id
                                LEFT OUTER JOIN mineral_history mhis ON ml_.id = mhis.mineral_id
                            ) temp_ WHERE temp_.discovery_year_min IS NOT NULL OR temp_.discovery_year_max IS NOT NULL
                        )
                    ELSE
                        (
                            SELECT to_json(temp_) AS history_ FROM (
                                SELECT mhis.discovery_year_min, mhis.discovery_year_max
                                FROM mineral_history mhis
                                WHERE mhis.mineral_id = ml.id
                            ) temp_ WHERE temp_.discovery_year_min IS NOT NULL OR temp_.discovery_year_max IS NOT NULL
                        )
                END AS history_
                FROM ("""
                + sql
                + """) ml;
                """,
                params,
            )

        if page is not None:
            serializer = self.get_serializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
