from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import render
from api.models import *
from api.serializers import *
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny


class mineral_basic(APIView):
    """
    A view which provides the basic details + history node on every mineral
    """
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_object(self, pk):
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=pk)
        except MineralList.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        print(request)
        queryset = self.get_object(pk)
        serializer = MineralListSerializer(queryset)
        return Response(serializer.data)

    def get_queryset(self):  
        queryset = MineralList.objects.all()
        # Set up eager loading to avoid N+1 selects
        queryset = queryset.select_related('id_class', 'id_subclass', 'id_family', 'history',)
        queryset = queryset.prefetch_related('status',)
        return queryset

class mineral_history(APIView):
    """
    A view which provides the details on history node of mineral
    """
    def get_object(self, pk):
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=pk)
        except MineralList.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = MineralHistoryNodeSerializer(queryset)
        return Response(serializer.data)

    def get_queryset(self):  
        queryset = MineralList.objects.all()
        # Set up eager loading to avoid N+1 selects
        queryset = queryset.select_related('history',)
        return queryset

class mineral_relation(APIView):
    """
    A view which provides the details on relations node of mineral
    """
    def get_object(self, pk):
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=pk)
        except MineralList.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        queryset = self.get_object(pk).relations
        serializer = MineralRelationSerializer(queryset, read_only=True)
        return Response(serializer.data)

    def get_queryset(self):  
        queryset = MineralList.objects.all()
        return queryset

class mineralClassification(APIView):
    """
    A view which provides the details on classification node of mineral
    """
    def get_object(self, pk):
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=pk)
        except MineralList.DoesNotExist:
            return Response('Mineral doesn\'t exist')

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = mineralClassificationSerializer(queryset, read_only=True)
        return Response(serializer.data)

    def get_queryset(self):  
        queryset = MineralList.objects.all()
        # Set up eager loading to avoid N+1 selects
        queryset = queryset.select_related('id_class', 'id_subclass', 'id_family',)
        return queryset

class group_first_children(APIView):
    """
    the view which outputs first children of supergroup, group, subgroup, root or series
    """
    permission_classes = [AllowAny]
    serializer_class = groupFirstChildrenSerializer

    def get_queryset(self):  
        queryset = MineralHierarchy.objects.all()
        queryset_prefetch = self.serializer_class.setup_eager_loading(queryset)
        return queryset_prefetch

    def get(self, request, pk):
        """ READ part """
        try:
            queryset = self.get_queryset().filter(parent_id=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except MineralHierarchy.DoesNotExist:
            return Response("Entry in mineral_hierarchy doesn't exist.", status=status.HTTP_404_NOT_FOUND)