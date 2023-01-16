# -*- coding: UTF-8 -*-
from rest_framework import serializers


class SVGSerializer(serializers.Serializer):
    file = serializers.FileField()
