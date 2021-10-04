from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import render
from api.models import *
from stats.serializers import *
from stats.functions.stats import *
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings

# Create your views here.
class statusCounts(APIView):
    """
    View to get status counts
    Args: 
        type: 'basic' or 'descriptive', which would produce a basic or a descriptive stats for statuses_list db table
    """
    queryset = MineralStatus.objects
    serializer_class = statusCountsSerializer
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    def get(self, request):
        count_type = request.GET['count_type'] if 'count_type' in request.GET else 'basic'
        view_type = request.GET['view_type'] if 'view_type' in request.GET else 'default'
        context_data = {'view_type': view_type}
        output = status_counts(self.queryset, count_type=count_type, view_type=view_type)
        serializer = statusCountsSerializer(output, many=True, context=context_data)
        return Response(serializer.data)

class discoveryYearCounts(APIView):
    """
    View to get discovery counts
    """
    queryset = MineralHistory.objects
    serializer_class = discoveryYearCountsSerializer
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    def get(self, request):
        min = request.GET['min'] if 'min' in request.GET else 1800
        max = request.GET['max'] if 'max' in request.GET else None

        output = discovery_year_counts(self.queryset, min=min, max=max)
        serializer = discoveryYearCountsSerializer(output, many=True)
        return Response(serializer.data)


class discoveryCountryCounts(APIView):
    """
    View to get discovery country counts
    """
    queryset = MineralCountry.objects
    serializer_class = discoveryCountryCountsSerializer
    # renderer_classes = [JSONRenderer]
    # parser_classes = [JSONParser]

    def get(self, request):

        output = discovery_country_counts(self.queryset)
        serializer = discoveryCountryCountsSerializer(output, many=True)
        return Response(serializer.data)

    def dispatch(self, *args, **kwargs):
        return super(discoveryCountryCounts, self).dispatch(*args, **kwargs)