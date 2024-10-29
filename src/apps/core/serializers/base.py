from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        fields = [
            "id",
            "name",
        ]
