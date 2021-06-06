from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.decorators import method_decorator
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from api.models import *
from decimal import *
import json
from django.db.models import Q, Count
from api.stats.functions.stats import *
from api.stats.serializers import *


# Create your views here.

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

# @method_decorator(cache_page(CACHE_TTL), name='dispatch')
class homepage(TemplateView):
    template_name = 'web/homepage.html'
    queryset = MineralStatus.objects

    def get(self, request, *args, **kwargs):
        # print("IP Address for debug-toolbar: " + request.META['REMOTE_ADDR'])
        counts = status_counts(self.queryset, count_type='basic')
        serializer = statusCountsSerializer(counts, many=True, context={'view_type': 'default'})
        return TemplateResponse(request, self.template_name, { 'counts': serializer.data })

class mineral_stats(TemplateView):
    template_name = 'web/mineral_stats.html'
    queryset = MineralStatus.objects

    def get(self, request, *args, **kwargs):
        # print("IP Address for debug-toolbar: " + request.META['REMOTE_ADDR'])
        counts = status_counts(self.queryset, count_type='descriptive', view_type='nested')
        serializer = statusCountsSerializer(counts, many=True, context={'view_type': 'nested'})
        return TemplateResponse(request, self.template_name, { 'counts': serializer.data })

class contact(TemplateView):
    template_name = 'web/contact.html'
    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name)

class about(TemplateView):
    template_name = 'web/about.html'
    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name)

class api(TemplateView):
    template_name = 'web/api.html'
    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name)