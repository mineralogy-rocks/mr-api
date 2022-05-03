from django.db import models
from rest_framework import serializers

from ..models.crystal import CrystalSystem


class CrystalSystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrystalSystem
        fields = ['id', 'name',]
