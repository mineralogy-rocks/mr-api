# -*- coding: UTF-8 -*-
from dal import autocomplete
from django.conf import settings
from django.contrib.postgres.expressions import ArraySubquery
from django.db import OperationalError
from django.db import connection
from django.db import transaction
from django.db.models import Case
from django.db.models import CharField
from django.db.models import Count
from django.db.models import Exists
from django.db.models import F
from django.db.models import Subquery
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat
from django.db.models.functions import JSONObject
from django.db.models.functions import Right
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import DetailView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination, CursorPagination
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
from .models.mineral import MindatSync, MineralRelation
from .models.mineral import Mineral
from .models.mineral import MineralCrystallography
from .models.mineral import MineralStatus
from .serializers.core import NsClassSubclassFamilyListSerializer
from .serializers.core import NsFamilyListSerializer
from .serializers.core import NsSubclassListSerializer
from .serializers.core import StatusListSerializer
from .serializers.mineral import MineralListSerializer
from .serializers.mineral import MineralRetrieveSerializer


class MindatSyncView(DetailView):

    template_name = "sync/sync-detail.html"
    model = MindatSync
    context_object_name = "sync_object"

    def get_context_data(self, **kwargs):
        object = self.get_object()
        context = super().get_context_data(**kwargs)
        context["base_url"] = f"{settings.SCHEMA}://{settings.BACKEND_DOMAIN}"
        context["link"] = reverse("admin:core_mindatsync_change", kwargs={"object_id": object.id})

        return context


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


class OptimizedPaginator(LimitOffsetPagination):
    """
    Combination of ideas from:
     - https://gist.github.com/safar/3bbf96678f3e479b6cb683083d35cb4d
     - https://medium.com/@hakibenita/optimizing-django-admin-paginator-53c4eb6bfca3
    Overrides the count method of QuerySet objects to avoid timeouts.
    - Try to get the real count limiting the queryset execution time to 150 ms.
    - If count takes longer than 150 ms the database kills the query and raises OperationError. In that case,
    get an estimate instead of actual count when not filtered (this estimate can be stale and hence not fit for
    situations where the count of objects actually matter).
    - If any other exception occured fall back to default behaviour.
    """

    def get_count(self, queryset):
        """
        Returns an estimated number of objects, across all pages.
        """
        print(queryset.model._meta.db_table)
        # try:
        #     with transaction.atomic(), connection.cursor() as cursor:
        #         # Limit to 150 ms
        #         cursor.execute("SET LOCAL statement_timeout TO 100;")
        #         return self.get_count_(queryset)
        # except OperationalError:
        #     pass

        # if not queryset.query.where:
        try:
            print(queryset.model._meta.db_table)
            with transaction.atomic(), connection.cursor() as cursor:
                # Obtain estimated values (only valid with PostgreSQL)
                cursor.execute(
                    "SELECT reltuples FROM pg_class WHERE relname = %s",
                    [queryset.model._meta.db_table],
                )
                estimate = int(cursor.fetchone()[0])
                return estimate
        except Exception:
            # If any other exception occurred fall back to default behaviour
            pass
        return self.get_count_(queryset)

    def get_count_(self, queryset):
        """
        Determine an object count, supporting either querysets or regular lists.
        """
        try:
            return queryset.count()
        except (AttributeError, TypeError):
            return len(queryset)


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

        isostructural_minerals_ = (
            NsFamily.objects.values("ns_family").annotate(count=Count("minerals")).filter(id=OuterRef("ns_family"))
        )

        relations_count_ = (
            MineralRelation.objects.values("relation")
            .filter(Q(status__direct_status=True))
            .annotate(
                varieties_count=Case(
                    When(status__status__status_group__name="varieties", then=Count("relation")), default=Value(None)
                ),
                polytypes_count=Case(
                    When(status__status__status_group__name="polytypes", then=Count("relation")), default=Value(None)
                ),
            )
            .filter(mineral=OuterRef("id"))
        )

        crystal_systems_ = (
            MineralCrystallography.objects.values("crystal_system")
            .filter(Q(mineral__parents_hierarchy__parent=OuterRef("id")))
            .annotate(
                crystal_systems_=JSONObject(
                    id=F("crystal_system__id"), name=F("crystal_system__name"), count=Count("mineral", distinct=True)
                )
            )
        )

        is_grouping_ = MineralStatus.objects.filter(Q(mineral=OuterRef("id")) & Q(status__status_group=1))

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
            relations_=JSONObject(
                isostructural_minerals=Subquery(isostructural_minerals_.values('count')),
                varieties=Subquery(relations_count_.values('varieties_count')),
                polytypes=Subquery(relations_count_.values('polytypes_count')),
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

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response

    def list_(self, request, *args, **kwargs):
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
                                    SELECT COUNT(mr.id) AS counts, to_jsonb(sgl) AS status_group
                                    FROM mineral_status ms
                                    LEFT JOIN mineral_relation mr ON ms.id = mr.mineral_status_id
                                    INNER JOIN status_list sl ON ms.status_id = sl.id
                                    INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
                                    WHERE ms.direct_status AND
                                        ms.mineral_id = ml.id AND
                                        sgl.id  IN (1, 4)
                                    GROUP BY sgl.id
                                    UNION
                                    SELECT count(ml_.id) AS counts, (SELECT to_jsonb(sgl) AS status_group FROM status_group_list sgl WHERE sgl.id = 11)
                                    FROM ns_family nf
                                    INNER JOIN mineral_log ml_ ON nf.id = ml_.ns_family
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
                                SELECT MIN(mhis.discovery_year) AS discovery_year_min, MAX(mhis.discovery_year) AS discovery_year_max,
                                MIN(mhis.ima_year) AS ima_year_min, MAX(mhis.ima_year) AS ima_year_max,
                                MIN(mhis.publication_year) AS publication_year_min, MAX(mhis.publication_year) AS publication_year_max,
                                MIN(mhis.approval_year) AS approval_year_min, MAX(mhis.approval_year) AS approval_year_max
                                FROM mineral_hierarchy mh
                                INNER JOIN mineral_log ml_ ON mh.mineral_id = ml_.id AND mh.parent_id = ml.id
                                LEFT OUTER JOIN mineral_history mhis ON ml_.id = mhis.mineral_id
                            ) temp_ WHERE COALESCE(temp_.discovery_year_min, temp_.ima_year_min, temp_.publication_year_min, temp_.approval_year_min) IS NOT NULL
                        )
                    ELSE
                        (
                            SELECT to_json(temp_) AS history_ FROM (
                                SELECT mhis.discovery_year, mhis.ima_year, mhis.publication_year, mhis.approval_year
                                FROM mineral_history mhis
                                WHERE mhis.mineral_id = ml.id
                            ) temp_ WHERE COALESCE(temp_.discovery_year, temp_.ima_year, temp_.publication_year, temp_.approval_year) IS NOT NULL
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
