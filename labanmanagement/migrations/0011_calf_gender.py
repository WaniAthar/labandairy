# Generated by Django 4.2.5 on 2023-10-14 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labanmanagement', '0010_alter_calf_breed_alter_cow_breed'),
    ]

    operations = [
        migrations.AddField(
            model_name='calf',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default=1, max_length=10),
            preserve_default=False,
        ),
    ]
