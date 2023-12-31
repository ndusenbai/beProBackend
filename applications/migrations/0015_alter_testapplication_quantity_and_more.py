# Generated by Django 4.0.5 on 2022-09-05 09:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0014_testapplication_used_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testapplication',
            name='quantity',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='testapplication',
            name='used_quantity',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
