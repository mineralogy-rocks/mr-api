# -*- coding: UTF-8 -*-
from core.models.base import BaseModel
from core.models.base import Creatable
from core.models.base import Nameable
from core.models.base import Updatable
from django.db import models


class Tag(BaseModel, Nameable):

    class Meta:
        db_table = "tag"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Category(BaseModel, Nameable):

    class Meta:
        db_table = "category"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Post(BaseModel, Nameable, Creatable, Updatable):

    description = models.CharField(max_length=200)
    content = models.TextField()

    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    tags = models.ManyToManyField(Tag, related_name="posts")
    category = models.ForeignKey(Category, related_name="posts", on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "post"
        ordering = ["id"]

    def __str__(self):
        return self.name
