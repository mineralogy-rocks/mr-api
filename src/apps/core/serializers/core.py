# -*- coding: UTF-8 -*-
from rest_framework import serializers

from ..models.core import StatusGroup, Status, Country, RelationType


class StatusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusGroup
        fields = [
            "id",
            "name",
        ]


class StatusListSerializer(serializers.ModelSerializer):

    status_group = StatusGroupSerializer()

    class Meta:
        model = Status
        fields = [
            "status_id",
            "status_group",
            "description_short",
            "description_long",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")
        request = kwargs.get("request")

        select_related = [
            "status_group",
        ]

        queryset = queryset.select_related(*select_related)
        return queryset


class CountryListSerializer(serializers.ModelSerializer):

    iso_code = serializers.CharField(source="alpha_2")

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "region",
            "iso_code",
        ]


class RelationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationType
        fields = ["type", "note"]
