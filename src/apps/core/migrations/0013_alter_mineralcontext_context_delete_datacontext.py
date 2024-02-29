# Generated by Django 4.1.3 on 2024-02-03 19:13

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_mineralinheritance_mineral_inh_mineral_759164_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mineralcontext",
            name="context",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Physical Properties"), (2, "Optical Properties")], db_column="context_id", default=None
            ),
        ),
        migrations.DeleteModel(
            name="DataContext",
        ),
    ]