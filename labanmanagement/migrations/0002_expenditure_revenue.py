# Generated by Django 4.2.2 on 2023-09-04 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labanmanagement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expenditure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('paritculars', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('remarks', models.TextField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Revenue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('revenue', models.DecimalField(decimal_places=3, max_digits=100)),
            ],
        ),
    ]
