
from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .documents import MineralLogDocument

class MineralLogDocumentSerializer(DocumentSerializer):
    """Serializer for the MineralLog document."""
    # status = serializers.SerializerMethodField()

    class Meta(object):
        """Meta options."""

        # Specify the correspondent document class
        document = MineralLogDocument

        # List the serializer fields. Note, that the order of the fields
        # is preserved in the ViewSet.
        fields = (
            'mineral_id',
            'mineral_name',
            'formula',
            'ns_index',
            'status'
        )

    # def get_status(self, obj):
    #     if obj.status:
    #         return ';'.join([str(mineral_status.status_id) for mineral_status in obj.status])
    #     else:
    #         return []