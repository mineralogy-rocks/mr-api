# -*- coding: UTF-8 -*-
from rest_framework import serializers

from ..models.crystal import CrystalClass
from ..models.crystal import CrystalSystem
from ..models.crystal import SpaceGroup


class CrystalSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrystalSystem
        fields = [
            "id",
            "name",
        ]


class CrystalSystemsStatsSerializer(CrystalSystemSerializer):
    count = serializers.IntegerField()

    class Meta:
        model = CrystalSystem
        fields = CrystalSystemSerializer.Meta.fields + ["count"]


class CrystalClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrystalClass
        fields = [
            "id",
            "name",
        ]


class SpaceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceGroup
        fields = [
            "id",
            "name",
        ]
