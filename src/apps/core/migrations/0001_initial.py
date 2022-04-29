# Generated by Django 4.0.4 on 2022-04-29 07:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BondingType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Bonding Type',
                'verbose_name_plural': 'Bonding Types',
                'db_table': 'bonding_type_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ChemicalGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Chemical Group',
                'verbose_name_plural': 'Chemical Groups',
                'db_table': 'chemical_group_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('alpha_2', models.CharField(max_length=10, null=True)),
                ('alpha_3', models.CharField(max_length=10, null=True)),
                ('country_code', models.IntegerField(null=True)),
                ('region', models.CharField(max_length=100, null=True)),
                ('sub_region', models.CharField(max_length=100, null=True)),
                ('intermediate_region', models.CharField(max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
                'db_table': 'country_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('element', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=20)),
                ('atomic_number', models.IntegerField()),
                ('name_alternative', models.CharField(max_length=20, null=True)),
                ('atomic_mass', models.DecimalField(decimal_places=12, max_digits=15)),
                ('atomic_mass_standard_uncertainty', models.IntegerField(null=True)),
                ('electronic_configuration', models.CharField(max_length=30)),
                ('cpk_hex_color', models.CharField(max_length=6, null=True)),
                ('electronegativity', models.DecimalField(decimal_places=2, max_digits=3, null=True)),
                ('empirical_atomic_radius', models.IntegerField(null=True)),
                ('calculated_atomic_radius', models.IntegerField(null=True)),
                ('van_der_waals_radius', models.IntegerField(null=True)),
                ('covalent_single_bond_atomic_radius', models.IntegerField(null=True)),
                ('covalent_triple_bond_atomic_radius', models.IntegerField(null=True)),
                ('metallic_atomic_radius', models.IntegerField(null=True)),
                ('ion_radius', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('ion_radius_charge', models.CharField(max_length=5, null=True)),
                ('ionization_energy', models.IntegerField(null=True)),
                ('electron_affinity', models.IntegerField(null=True)),
                ('oxidation_states', models.CharField(max_length=50, null=True)),
                ('melting_point', models.IntegerField(null=True)),
                ('boiling_point', models.IntegerField(null=True)),
                ('density', models.DecimalField(decimal_places=6, max_digits=8, null=True)),
                ('crust_crc_handbook', models.DecimalField(decimal_places=10, max_digits=11, null=True)),
                ('crust_kaye_laby', models.DecimalField(decimal_places=10, max_digits=11, null=True)),
                ('crust_greenwood', models.DecimalField(decimal_places=10, max_digits=11, null=True)),
                ('crust_ahrens_taylor', models.DecimalField(decimal_places=10, max_digits=11, null=True)),
                ('crust_ahrens_wanke', models.DecimalField(decimal_places=10, max_digits=11, null=True)),
                ('crust_ahrens_waver', models.DecimalField(decimal_places=10, max_digits=11, null=True)),
                ('upper_crust_ahrens_taylor', models.DecimalField(decimal_places=10, max_digits=11, null=True)),
                ('upper_crust_ahrens_shaw', models.DecimalField(decimal_places=10, max_digits=11, null=True)),
                ('sea_water_crc_handbook', models.DecimalField(decimal_places=11, max_digits=11, null=True)),
                ('sea_water_kaye_laby', models.DecimalField(decimal_places=11, max_digits=11, null=True)),
                ('sun_kaye_laby', models.DecimalField(decimal_places=11, max_digits=16, null=True)),
                ('solar_system_kaye_laby', models.DecimalField(decimal_places=11, max_digits=16, null=True)),
                ('solar_system_ahrens', models.DecimalField(decimal_places=11, max_digits=16, null=True)),
                ('solar_system_ahrens_with_uncertainty', models.DecimalField(decimal_places=2, max_digits=4, null=True)),
                ('natural_isotopes', models.TextField(null=True)),
                ('name_meaning', models.TextField(null=True)),
                ('discovery_year', models.IntegerField(null=True)),
                ('discoverer', models.TextField(null=True)),
                ('application', models.TextField(null=True)),
                ('safety', models.TextField(null=True)),
                ('biological_role', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'ELement',
                'verbose_name_plural': 'Elements',
                'db_table': 'element_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GoldschmidtClass',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Goldschmidt Class',
                'verbose_name_plural': 'Goldschmidt Classes',
                'db_table': 'goldschmidt_class_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Ion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('formula', models.CharField(max_length=100)),
                ('formula_with_oxidation', models.CharField(max_length=100, null=True)),
                ('overall_charge', models.CharField(max_length=100, null=True)),
                ('expressed_as', models.TextField(blank=True, null=True)),
                ('element_or_sulfide', models.BooleanField(blank=True, null=True)),
                ('structure_description', models.TextField(blank=True, null=True)),
                ('geometry', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Ion',
                'verbose_name_plural': 'Ions',
                'db_table': 'ion_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IonClass',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Ion Class',
                'verbose_name_plural': 'Ion Classes',
                'db_table': 'ion_class_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IonElement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Ion Element',
                'verbose_name_plural': 'Ion Elements',
                'db_table': 'ion_element',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IonGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Ion Group',
                'verbose_name_plural': 'Ion Groups',
                'db_table': 'ion_group_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IonSubclass',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Ion Subclass',
                'verbose_name_plural': 'Ion Subclasses',
                'db_table': 'ion_subclass_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IonSubgroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Ion Subgroup',
                'verbose_name_plural': 'Ion Subgroups',
                'db_table': 'ion_subgroup_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IonSubunit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Ion Subunit',
                'verbose_name_plural': 'Ion Subunits',
                'db_table': 'ion_subunit',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IonType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Ion Type',
                'verbose_name_plural': 'Ion Types',
                'db_table': 'ion_type_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Mineral',
            fields=[
                ('name', models.CharField(max_length=200, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('formula', models.TextField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('ns_mineral', models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                'verbose_name': 'Mineral',
                'verbose_name_plural': 'Minerals',
                'db_table': 'mineral_log',
                'ordering': ['name'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MineralCountry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('note', models.TextField(blank=True, db_column='note', null=True)),
            ],
            options={
                'verbose_name': 'Discovery Country',
                'verbose_name_plural': 'Discovery Countries',
                'db_table': 'mineral_country',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MineralHierarchy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Hierarchy',
                'verbose_name_plural': 'Hierarchies',
                'db_table': 'mineral_hierarchy',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MineralHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('discovery_year_min', models.IntegerField(blank=True, null=True)),
                ('discovery_year_max', models.IntegerField(blank=True, null=True)),
                ('discovery_year_note', models.TextField(blank=True, null=True)),
                ('certain', models.BooleanField(default=True)),
                ('first_usage_date', models.TextField(blank=True, null=True)),
                ('first_known_use', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'MineralHistory',
                'db_table': 'mineral_history',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MineralImpurity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ion_quantity', models.CharField(blank=True, max_length=30, null=True)),
                ('rich_poor', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Impurity',
                'verbose_name_plural': 'Impurities',
                'db_table': 'mineral_impurity',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MineralIonTheoretical',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Theoretical Ion',
                'verbose_name_plural': 'Theoretical Ions',
                'db_table': 'mineral_ion_theoretical',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MineralRelation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('relation_note', models.TextField(blank=True, null=True)),
                ('direct_relation', models.BooleanField()),
            ],
            options={
                'verbose_name': 'Relation',
                'verbose_name_plural': 'Relations',
                'db_table': 'mineral_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MineralStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Status',
                'verbose_name_plural': 'Statuses',
                'db_table': 'mineral_status',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('note', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'Nationality',
                'verbose_name_plural': 'Nationalities',
                'db_table': 'nationality_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NsClass',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'Nickel-Strunz Class',
                'verbose_name_plural': 'Nickel-Strunz Classes',
                'db_table': 'ns_class',
                'ordering': ['id'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NsFamily',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ns_family', models.CharField(max_length=5, unique=True)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'Nickel-Strunz Family',
                'verbose_name_plural': 'Nickel-Strunz Families',
                'db_table': 'ns_family',
                'ordering': ['ns_class', 'ns_family'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NsSubclass',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ns_subclass', models.CharField(max_length=4, unique=True)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'Nickel-Strunz Subclass',
                'verbose_name_plural': 'Nickel-Strunz Subclasses',
                'db_table': 'ns_subclass',
                'ordering': ['ns_class', 'ns_subclass'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PhaseState',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Phase State',
                'verbose_name_plural': 'Phase States',
                'db_table': 'phase_state_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RelationType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('note', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Relation Type',
                'verbose_name_plural': 'Relation Types',
                'db_table': 'relation_type_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status_id', models.FloatField()),
                ('description_long', models.TextField(blank=True, null=True)),
                ('description_short', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Status',
                'verbose_name_plural': 'Statuses',
                'db_table': 'status_list',
                'ordering': ['status_id'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StatusGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Status Group',
                'verbose_name_plural': 'Status Groups',
                'db_table': 'status_group_list',
                'ordering': ['name'],
                'managed': False,
            },
        ),
    ]
