# -*- coding: UTF-8 -*-
from dal import autocomplete
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import Case
from django.db.models import CharField
from django.db.models import Count
from django.db.models import Exists
from django.db.models import F
from django.db.models import JSONField
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.db.models.expressions import RawSQL
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat
from django.db.models.functions import JSONObject
from django.db.models.functions import Right
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.pagination import CursorPagination
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_simplejwt.authentication import JWTAuthentication

from .filters import MineralFilter
from .filters import NickelStrunzFilter
from .filters import StatusFilter
from .models.core import NsClass
from .models.core import NsFamily
from .models.core import NsSubclass
from .models.core import Status
from .models.mineral import Mineral
from .models.mineral import MineralCrystallography
from .models.mineral import MineralStatus
from .serializers.core import NsClassSubclassFamilyListSerializer
from .serializers.core import NsFamilyListSerializer
from .serializers.core import NsSubclassListSerializer
from .serializers.core import StatusListSerializer
from .serializers.mineral import MineralListSerializer
from .serializers.mineral import MineralRetrieveSerializer


class MineralSearch(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Mineral.objects.none()

        qs = Mineral.objects.all()

        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q))

        return qs


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
    permission_classes = [HasAPIKey | IsAuthenticated]
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]

    ordering_fields = [
        "status_id",
        "group",
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
        "group__name",
    ]
    filterset_class = StatusFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, "setup_eager_loading"):
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)

        return queryset


class NickelStrunzViewSet(ListModelMixin, GenericViewSet):

    http_method_names = [
        "get",
        "options",
        "head",
    ]

    queryset = NsClass.objects.all()
    serializer_class = NsClassSubclassFamilyListSerializer

    renderer_classes = [
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    permission_classes = [HasAPIKey | IsAuthenticated]
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]

    pagination_class = LimitOffsetPagination

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "id",
        "description",
        "subclasses__description",
        "families__description",
        "subclasses__ns_subclass",
        "families__ns_family",
    ]
    filterset_class = NickelStrunzFilter

    def _get_paginated_response(self, queryset, serializer):
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(serializer(page, many=True).data)

        return Response(serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def _filter_queryset(self, queryset):
        if "q" in self.request.query_params:
            queryset = queryset.filter(description__icontains=self.request.query_params.get("q", ""))

        if "class" in self.request.query_params:
            queryset = queryset.filter(ns_class=self.request.query_params.get("class", ""))

        if "subclass" in self.request.query_params:
            if self.action in ["subclasses"]:
                queryset = queryset.filter(ns_subclass=self.request.query_params.get("subclass", ""))
            elif self.action in ["families"]:
                queryset = queryset.filter(ns_subclass__ns_subclass=self.request.query_params.get("subclass", ""))
            else:
                pass

        if "family" in self.request.query_params:
            if self.action in ["subclasses"]:
                queryset = queryset.filter(families__ns_family=self.request.query_params.get("family", ""))
            elif self.action in ["families"]:
                queryset = queryset.filter(ns_family=self.request.query_params.get("family", ""))
            else:
                pass
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, "setup_eager_loading"):
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)

        return queryset

    @action(methods=["get"], detail=False, url_path="classes")
    def classes(self, request, *args, **kwargs):
        queryset = NsClass.objects.annotate(counts=Count("minerals", distinct=True))
        queryset = self.filter_queryset(queryset)
        return Response(queryset.values("id", "description", "counts"), status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False, url_path="subclasses")
    def subclasses(self, request, *args, **kwargs):
        serializer_class = NsSubclassListSerializer
        queryset = (
            NsSubclass.objects.select_related("ns_class")
            .annotate(counts=Count("minerals", distinct=True))
            .order_by("ns_class__id", "ns_subclass")
        )
        queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)
        queryset = self._filter_queryset(queryset)

        return self._get_paginated_response(queryset, serializer_class)

    @action(methods=["get"], detail=False, url_path="families")
    def families(self, request, *args, **kwargs):
        serializer_class = NsFamilyListSerializer
        queryset = NsFamily.objects.annotate(counts=Count("minerals", distinct=True))

        queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)
        queryset = self._filter_queryset(queryset)

        return self._get_paginated_response(queryset, serializer_class)


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
    pagination_class = CursorPagination

    permission_classes = [HasAPIKey | IsAuthenticated]
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]

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
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)

        crystal_systems_ = (
            MineralCrystallography.objects.values("crystal_system")
            .filter(Q(mineral__parents_hierarchy__parent=OuterRef("id")))
            .annotate(
                crystal_systems_=JSONObject(
                    id=F("crystal_system__id"), name=F("crystal_system__name"), count=Count("mineral", distinct=True)
                )
            )
        )

        is_grouping_ = MineralStatus.objects.filter(Q(mineral=OuterRef("id")) & Q(status__group=1))

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

        queryset = queryset.annotate(
            crystal_systems_=Case(
                When(is_grouping=True, then=ArraySubquery(crystal_systems_.values("crystal_systems_"))), default=[]
            ),
            discovery_countries_=Case(
                When(
                    is_grouping=True,
                    then=RawSQL(
                        """
                        (
                            SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                                SELECT cl.id, cl.name, count(cl.id) AS counts
                                FROM mineral_country mc
                                INNER JOIN country_list cl ON mc.country_id = cl.id
                                INNER JOIN mineral_hierarchy mh ON mh.mineral_id = mc.mineral_id
                                WHERE mh.parent_id = mineral_log.id
                                AND cl.id <> 250
                                GROUP BY cl.id
                                ORDER BY counts DESC, name DESC
                                LIMIT 5
                            ) temp_
                        )
                    """,
                        (),
                    ),
                ),
                default=[],
            ),
            relations_=Case(
                When(
                    is_grouping=True,
                    then=RawSQL(
                        """
                            (
                                SELECT COALESCE(jsonb_agg(temp_), '[]'::jsonb)
                                FROM (
                                        WITH RECURSIVE hierarchy as (
                                            SELECT
                                                id,
                                                mineral_id,
                                                parent_id
                                            FROM mineral_hierarchy
                                            WHERE mineral_id = mineral_log.id
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
                                                to_jsonb(sgl) AS group
                                        FROM hierarchy h
                                        INNER JOIN mineral_status ms ON ms.mineral_id = h.mineral_id
                                        INNER JOIN status_list sl ON sl.id = ms.status_id
                                        INNER JOIN status_group_list sgl ON sgl.id = sl.status_group_id
                                        WHERE h.parent_id IS NOT NULL AND sgl.id IN (3, 11)
                                        GROUP BY sgl.id
                                ) temp_
                            )
                        """,
                        (),
                    ),
                ),
                default=RawSQL(
                    """
                        (
                            SELECT COALESCE(jsonb_agg(temp_), '[]'::jsonb)
                            FROM (
                                SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id, counts, status_group FROM (
                                    SELECT COUNT(mr.id) AS counts, to_jsonb(sgl) AS status_group
                                    FROM mineral_status ms
                                    LEFT JOIN mineral_relation mr ON ms.id = mr.mineral_status_id
                                    INNER JOIN status_list sl ON ms.status_id = sl.id
                                    INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
                                    WHERE ms.direct_status AND
                                        ms.mineral_id = mineral_log.id AND
                                        sgl.id IN (2, 3)
                                    GROUP BY sgl.id
                                    UNION
                                    SELECT COUNT(ml_.id) AS counts, (SELECT to_jsonb(sgl) AS status_group FROM status_group_list sgl WHERE sgl.id = 11)
                                    FROM mineral_log ml_
                                    INNER JOIN mineral_status ms ON ms.mineral_id = ml_.id
                                    WHERE ms.status_id = 1 AND ml_.ns_family = mineral_log.ns_family AND ml_.id <> mineral_log.id
                                    HAVING count(ml_.id) > 0
                                ) inner_
                            ) temp_
                        )
                    """,
                    (),
                ),
                output_field=JSONField(),
            ),
        )

        queryset = queryset.defer(
            "ns_class",
            "ns_subclass",
            "ns_mineral",
            "note",
            "created_at",
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
                    & Q(children_hierarchy__mineral__discovery_countries__in=discovery_countries.split(","))
                )

        else:
            if discovery_countries:
                queryset = queryset.filter(Q(discovery_countries__in=discovery_countries.split(",")))

        return queryset

    def get_serializer_class(self):

        if self.action in ["list"]:
            return MineralListSerializer
        elif self.action in ["retrieve"]:
            return MineralRetrieveSerializer

        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.seen += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
