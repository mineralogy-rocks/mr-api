# Generated by Django 5.0.2 on 2024-07-02 11:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_alter_mineralcontext_context_delete_datacontext"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="mineralinheritance",
            name="mineral_inh_mineral_759164_idx",
        ),
        migrations.RenameIndex(
            model_name="mineralinheritance",
            new_name="mineral_inh_prop_2c1c91_idx",
            old_name="mineral_inh_prop_id_c22b36_idx",
        ),
        migrations.AlterUniqueTogether(
            name="mineralrelation",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="mineralstatus",
            name="relations",
        ),
        migrations.AlterField(
            model_name="hierarchyview",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, related_name="hierarchy", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="hierarchyview",
            name="relation",
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to="core.mineral"),
        ),
        migrations.AlterField(
            model_name="mineral",
            name="ns_class",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="minerals",
                to="core.nsclass",
            ),
        ),
        migrations.AlterField(
            model_name="mineral",
            name="ns_family",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="minerals",
                to="core.nsfamily",
            ),
        ),
        migrations.AlterField(
            model_name="mineral",
            name="ns_subclass",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="minerals",
                to="core.nssubclass",
            ),
        ),
        migrations.AlterField(
            model_name="mineralcontext",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="contexts", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralcountry",
            name="country",
            field=models.ForeignKey(
                default=None, on_delete=django.db.models.deletion.CASCADE, related_name="minerals", to="core.country"
            ),
        ),
        migrations.AlterField(
            model_name="mineralcountry",
            name="mineral",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.mineral"),
        ),
        migrations.AlterField(
            model_name="mineralcrystallography",
            name="crystal_class",
            field=models.ForeignKey(
                default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.crystalclass"
            ),
        ),
        migrations.AlterField(
            model_name="mineralcrystallography",
            name="crystal_system",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="minerals",
                to="core.crystalsystem",
            ),
        ),
        migrations.AlterField(
            model_name="mineralcrystallography",
            name="mineral",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="crystallography",
                to="core.mineral",
            ),
        ),
        migrations.AlterField(
            model_name="mineralcrystallography",
            name="space_group",
            field=models.ForeignKey(
                default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.spacegroup"
            ),
        ),
        migrations.AlterField(
            model_name="mineralformula",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="formulas", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralformula",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="minerals", to="core.formulasource"
            ),
        ),
        migrations.AlterField(
            model_name="mineralhistory",
            name="mineral",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name="history", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralimanote",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="ima_notes", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralimastatus",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="ima_statuses", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralimpurity",
            name="ion",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.ion"),
        ),
        migrations.AlterField(
            model_name="mineralimpurity",
            name="mineral",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.mineral"),
        ),
        migrations.AlterField(
            model_name="mineralinheritance",
            name="inherit_from",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="descendants", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralinheritance",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="inheritance_chain", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralinheritance",
            name="prop",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Inherit Formula"), (2, "Inherit Crystal System"), (3, "Inherit Physical Properties")]
            ),
        ),
        migrations.AlterField(
            model_name="mineralionposition",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="ions", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralionposition",
            name="position",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.ionposition"),
        ),
        migrations.AlterField(
            model_name="mineraliontheoretical",
            name="ion",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="minerals_theoretical", to="core.ion"
            ),
        ),
        migrations.AlterField(
            model_name="mineraliontheoretical",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="ions_theoretical", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralrelation",
            name="mineral",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.mineral"),
        ),
        migrations.AlterField(
            model_name="mineralrelation",
            name="relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="inverse_relations", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralrelation",
            name="status",
            field=models.ForeignKey(
                db_column="mineral_status_id",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="relations",
                to="core.mineralstatus",
            ),
        ),
        migrations.AlterField(
            model_name="mineralrelationsuggestion",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="suggested_relations", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralrelationsuggestion",
            name="relation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="suggested_inverse_relations",
                to="core.mineral",
            ),
        ),
        migrations.AlterField(
            model_name="mineralrelationsuggestion",
            name="relation_type",
            field=models.IntegerField(help_text="Relation type according to mindat.", null=True),
        ),
        migrations.AlterField(
            model_name="mineralstatus",
            name="author",
            field=models.ForeignKey(
                help_text="Author of the last update.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="mineralstatus",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="mineral_statuses", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralstatus",
            name="status",
            field=models.ForeignKey(
                help_text="A classification status of species.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="minerals",
                to="core.status",
            ),
        ),
        migrations.AlterField(
            model_name="mineralstructure",
            name="amcsd",
            field=models.CharField(
                blank=True, help_text="American Mineralogist Crystal Structure Database id", max_length=50, null=True
            ),
        ),
        migrations.AlterField(
            model_name="mineralstructure",
            name="cod",
            field=models.IntegerField(blank=True, help_text="Open Crystallography Database id", null=True),
        ),
        migrations.AlterField(
            model_name="mineralstructure",
            name="mineral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="structures", to="core.mineral"
            ),
        ),
        migrations.AlterField(
            model_name="mineralstructure",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="structures", to="core.formulasource"
            ),
        ),
    ]
