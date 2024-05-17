# -*- coding: UTF-8 -*-
from rest_framework import serializers

from .models import Category
from .models import Post
from .models import Tag


class TagListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
        ]


class CategoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


class PostListSerializer(serializers.ModelSerializer):

    tags = TagListSerializer(many=True)
    category = CategoryListSerializer()
    url = serializers.HyperlinkedIdentityField(view_name="blog:post-detail", lookup_field="slug")

    class Meta:
        model = Post
        fields = [
            "id",
            "name",
            "slug",
            "url",
            "description",
            "views",
            "likes",
            "tags",
            "category",
            "published_at",
        ]

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


class PostDetailSerializer(serializers.ModelSerializer):

    tags = TagListSerializer(many=True)
    category = CategoryListSerializer()

    class Meta:
        model = Post
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "content",
            "views",
            "likes",
            "tags",
            "category",
            "created_at",
            "updated_at",
            "is_published",
            "published_at",
        ]
        depth = 1
