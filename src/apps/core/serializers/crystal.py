# -*- coding: UTF-8 -*-
from rest_framework import serializers

from ..models.crystal import CrystalSystem


class CrystalSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrystalSystem
        fields = [
            "id",
            "name",
        ]


class CrystalSystemsStatsSerializer(CrystalSystemSerializer):

    counts = serializers.IntegerField()

    class Meta:
        model = CrystalSystem
        fields = CrystalSystemSerializer.Meta.fields + ["counts"]
