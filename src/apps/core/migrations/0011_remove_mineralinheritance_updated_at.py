# Generated by Django 4.1.3 on 2023-12-15 19:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_remove_mineralcrystallography_inherited_from_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mineralinheritance",
            name="updated_at",
        ),
    ]
