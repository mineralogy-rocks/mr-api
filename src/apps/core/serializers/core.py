from rest_framework import serializers

from ..models.core import StatusGroup, Status, Country, RelationType


class StatusGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusGroup
        fields = ['id', 'name',]



class StatusListSerializer(serializers.ModelSerializer):

    status_group = StatusGroupSerializer()

    class Meta:
        model = Status
        fields = ['id', 'status_id', 'status_group', 'description_short', 'description_long',]



class CountryListSerializer(serializers.ModelSerializer):

    iso_code = serializers.CharField(source='alpha_2')

    class Meta:
        model = Country
        fields = ['id', 'name', 'region', 'iso_code',]



class RelationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelationType
        fields = ['type', 'note']
