# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Prefetch

from .models import Category
from .models import Post
from .models import Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ["id", "name"]
    search_fields = ["name"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related(
            Prefetch(
                "posts",
                queryset=Post.objects.annotate(
                    has_posts=Exists(Post.objects.filter(category=OuterRef("pk")).only("id"))
                ),
            )
        )
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ["id", "name"]
    search_fields = ["name"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related(
            Prefetch(
                "posts",
                queryset=Post.objects.annotate(has_posts=Exists(Post.objects.filter(tags=OuterRef("pk")).only("id"))),
            )
        )
        return queryset


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    date_hierarchy = "created_at"

    list_display = [
        "id",
        "name",
        "category",
        "tags_",
        "is_published",
        "published_at",
    ]
    list_filter = [
        "is_published",
        "category",
        "tags",
    ]

    list_display_links = ["name"]

    readonly_fields = [
        "id",
        "views",
        "likes",
        "created_at",
        "updated_at",
    ]
    fieldsets = [
        (None, {"fields": ["id", "name", "slug", "is_published"]}),
        ("Description", {"fields": ["description"], "classes": ["full-width"]}),
        ("Content", {"fields": ["content"], "classes": ["full-width", "full-height"]}),
        ("Context", {"fields": ["category", "tags"]}),
        ("Timestamps", {"fields": ["created_at", "updated_at"]}),
        (
            "Metadata",
            {
                "fields": [
                    "views",
                    "likes",
                    "published_at",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    @admin.display(description="Tags")
    def tags_(self, instance):
        if instance.tags:
            return ", ".join([tag.name for tag in instance.tags.all()])
