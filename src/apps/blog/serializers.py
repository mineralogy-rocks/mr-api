# -*- coding: UTF-8 -*-
from core.serializers.base import BaseSerializer

from .models import Category
from .models import Post
from .models import Tag


class TagListSerializer(BaseSerializer):

    class Meta:
        model = Tag
        fields = BaseSerializer.Meta.fields + []


class CategoryListSerializer(BaseSerializer):

    class Meta:
        model = Category
        fields = BaseSerializer.Meta.fields + []


class PostListSerializer(BaseSerializer):

    tags = TagListSerializer(many=True)
    category = CategoryListSerializer()

    class Meta:
        model = Post
        fields = BaseSerializer.Meta.fields + [
            "description",
            "content",
            "views",
            "likes",
            "tags",
            "category",
        ]
        depth = 1

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = [
            "category",
        ]
        prefetch_related = [
            "tags",
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


class PostDetailSerializer(BaseSerializer):

    class Meta:
        model = Post
        fields = BaseSerializer.Meta.fields + [
            "description",
            "content",
            "views",
            "likes",
            "tags",
            "category",
        ]
        depth = 1
