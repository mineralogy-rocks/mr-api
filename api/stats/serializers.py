from rest_framework import serializers
from django.db.models import Q, F
from decimal import *
from api.models import *

class baseStatusCountsSerializer(serializers.Serializer):
    status_id = serializers.DecimalField(read_only=True, max_digits=4, decimal_places=2)
    mineral_counts = serializers.IntegerField(read_only=True)
    description_group = serializers.CharField(read_only=True)
    description_short = serializers.CharField(read_only=True)

    class Meta:
        fields=('status_id', 'mineral_counts', 'description_short', 'description_short',)

class statusCountsSerializer(serializers.Serializer):

    def to_representation(self, instance):
        if (self.context['view_type'] == 'nested'):
            output = {
                'group': instance['group'],
                'statuses': baseStatusCountsSerializer(instance['statuses'], many=True).data
            }
        else:
            output = {
                'status_id': instance['status_id'],
                'mineral_counts': instance['mineral_counts'],
                'description_group': instance['description_group'],
                'description_short': instance['description_short']
            }

        return output

class discoveryYearCountsSerializer(serializers.Serializer):
    mineral_counts = serializers.IntegerField(read_only=True)
    discovery_year = serializers.IntegerField(read_only=True)

    class Meta:
        fields=('mineral_counts', 'discovery_year',)


class discoveryCountryCountsSerializer(serializers.Serializer):
    country_id = serializers.IntegerField(read_only=True)
    country_name = serializers.CharField(read_only=True)
    country_iso = serializers.CharField(read_only=True)
    mineral_count = serializers.IntegerField(read_only=True)

    class Meta:
        fields=('country_id', 'country_name', 'country_iso', 'mineral_count',)