# -*- coding: UTF-8 -*-
from django_filters import rest_framework as filters

from .models import Post


class PostFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name="category__slug",
        lookup_expr="exact",
    )

    class Meta:
        model = Post
        fields = ["name", "views", "likes", "tags", "category"]
