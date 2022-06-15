# Generated by Django 4.0.5 on 2022-06-15 10:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_alter_department_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=22, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='department',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=22, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
