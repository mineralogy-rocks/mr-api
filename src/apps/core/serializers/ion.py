# -*- coding: UTF-8 -*-
from rest_framework import serializers

from ..models.ion import Ion, IonPosition
from ..models.mineral import MineralIonPosition


class IonPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IonPosition
        fields = [
            "id",
            "name",
        ]


class IonPrimitiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ion
        fields = [
            "id",
            "formula",
        ]


class MineralIonPositionSerializer(serializers.ModelSerializer):

    ion = IonPrimitiveSerializer()
    position = IonPositionSerializer()

    class Meta:
        model = IonPosition
        fields = [
            "ion",
            "position",
        ]
