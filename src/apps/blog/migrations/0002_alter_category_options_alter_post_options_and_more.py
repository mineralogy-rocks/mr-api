# Generated by Django 5.0.2 on 2024-03-02 16:23

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ["id"], "verbose_name": "Category", "verbose_name_plural": "Categories"},
        ),
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ["id"], "verbose_name": "Post", "verbose_name_plural": "Posts"},
        ),
        migrations.AlterModelOptions(
            name="tag",
            options={"ordering": ["id"], "verbose_name": "Tag", "verbose_name_plural": "Tags"},
        ),
        migrations.AddField(
            model_name="post",
            name="is_published",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="post",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="post",
            name="slug",
            field=models.SlugField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
