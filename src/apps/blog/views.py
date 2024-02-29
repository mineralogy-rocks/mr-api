# -*- coding: UTF-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Category
from .models import Post
from .models import Tag
from .serializers import CategoryListSerializer
from .serializers import PostDetailSerializer
from .serializers import PostListSerializer
from .serializers import TagListSerializer


class TagViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):

    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = ["name"]
    ordering_fields = ["id", "name"]
    ordering = ["id"]


class CategoryViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):

    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = ["name"]
    ordering_fields = ["id", "name"]
    ordering = ["id"]


class PostViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):

    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = ["name", "description", "content", "views", "likes", "tags", "category"]
    ordering_fields = ["id", "name", "description", "content", "views", "likes", "tags", "category"]
    ordering = ["id"]

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, "setup_eager_loading"):
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer
