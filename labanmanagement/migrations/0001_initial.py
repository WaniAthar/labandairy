# Generated by Django 4.2.2 on 2023-08-13 07:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_id', models.CharField(max_length=255)),
                ('nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('dob', models.DateField()),
                ('father', models.CharField(blank=True, max_length=255)),
                ('breed', models.CharField(choices=[('HF', 'Holstein Friesian (HF)'), ('Jersey', 'Jersey'), ('Guernsey', 'Guernsey'), ('Ayrshire', 'Ayrshire'), ('Brown Swiss', 'Brown Swiss'), ('Milking Shorthorn', 'Milking Shorthorn'), ('Dutch Belted', 'Dutch Belted'), ('Red and White Holstein', 'Red and White Holstein'), ('Friesian', 'Friesian'), ('Montbéliarde', 'Montbéliarde'), ('Normande', 'Normande'), ('Swedish Red', 'Swedish Red'), ('Danish Red', 'Danish Red'), ('Ayshire', 'Ayshire'), ('Canadienne', 'Canadienne'), ('Shorthorn', 'Shorthorn'), ('Simmental', 'Simmental'), ('Gelbvieh', 'Gelbvieh'), ('Fleckvieh', 'Fleckvieh'), ('Norwegian Red', 'Norwegian Red'), ('Finnish Ayrshire', 'Finnish Ayrshire'), ('South Devon', 'South Devon'), ('Holstein-Sahiwal', 'Holstein-Sahiwal'), ('Meuse-Rhine-Issel', 'Meuse-Rhine-Issel'), ('British Friesian', 'British Friesian'), ('Kostroma', 'Kostroma'), ('Kholmogory', 'Kholmogory'), ('Red Poll', 'Red Poll'), ('Murray Grey', 'Murray Grey'), ('Chianina', 'Chianina'), ('Charolais', 'Charolais'), ('Simbrah', 'Simbrah')], max_length=100)),
                ('remarks', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_id', models.CharField(max_length=255)),
                ('nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('date_of_arrival', models.DateField()),
                ('breed', models.CharField(choices=[('HF', 'Holstein Friesian (HF)'), ('Jersey', 'Jersey'), ('Guernsey', 'Guernsey'), ('Ayrshire', 'Ayrshire'), ('Brown Swiss', 'Brown Swiss'), ('Milking Shorthorn', 'Milking Shorthorn'), ('Dutch Belted', 'Dutch Belted'), ('Red and White Holstein', 'Red and White Holstein'), ('Friesian', 'Friesian'), ('Montbéliarde', 'Montbéliarde'), ('Normande', 'Normande'), ('Swedish Red', 'Swedish Red'), ('Danish Red', 'Danish Red'), ('Ayshire', 'Ayshire'), ('Canadienne', 'Canadienne'), ('Shorthorn', 'Shorthorn'), ('Simmental', 'Simmental'), ('Gelbvieh', 'Gelbvieh'), ('Fleckvieh', 'Fleckvieh'), ('Norwegian Red', 'Norwegian Red'), ('Finnish Ayrshire', 'Finnish Ayrshire'), ('South Devon', 'South Devon'), ('Holstein-Sahiwal', 'Holstein-Sahiwal'), ('Meuse-Rhine-Issel', 'Meuse-Rhine-Issel'), ('British Friesian', 'British Friesian'), ('Kostroma', 'Kostroma'), ('Kholmogory', 'Kholmogory'), ('Red Poll', 'Red Poll'), ('Murray Grey', 'Murray Grey'), ('Chianina', 'Chianina'), ('Charolais', 'Charolais'), ('Simbrah', 'Simbrah')], max_length=30)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('offspring', models.ManyToManyField(blank=True, related_name='parents', to='labanmanagement.calf')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('phone_no', models.IntegerField()),
                ('qty', models.IntegerField()),
                ('rate', models.IntegerField()),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DailyTotalMilk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('total_milk', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('sold_milk', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('remaining_milk', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='PayAsYouGoCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('qty', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('paid', models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=100, null=True)),
                ('balance', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('remarks', models.TextField(blank=True)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='MilkProduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('morning_milk_quantity', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('evening_milk_quantity', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('morning_time', models.TimeField(blank=True, null=True)),
                ('evening_time', models.TimeField(blank=True, null=True)),
                ('total_milk', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('cow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labanmanagement.cow')),
            ],
        ),
        migrations.CreateModel(
            name='Medication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('Diagnosis', models.TextField()),
                ('doctor', models.CharField(default='Dr. ', max_length=255)),
                ('Medication', models.CharField(max_length=255)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('cows', models.ManyToManyField(related_name='medications', to='labanmanagement.cow')),
            ],
        ),
        migrations.CreateModel(
            name='HeatPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('cow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='heat_periods', to='labanmanagement.cow')),
            ],
        ),
        migrations.CreateModel(
            name='HandleCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('qty', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('paid', models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=100, null=True)),
                ('balance', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('remarks', models.TextField(blank=True)),
                ('date', models.DateField()),
                ('laag_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labanmanagement.customer')),
            ],
        ),
        migrations.CreateModel(
            name='DryPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('cow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dry_periods', to='labanmanagement.cow')),
            ],
        ),
        migrations.AddField(
            model_name='calf',
            name='mother',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='calves_as_mother', to='labanmanagement.cow'),
        ),
        migrations.CreateModel(
            name='BirthEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('calf_name', models.CharField(max_length=100)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('mother', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calves', to='labanmanagement.cow')),
            ],
        ),
    ]
