# Generated by Django 4.0.5 on 2022-06-17 11:04

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0009_role_unique role in company for user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='grade',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)]),
        ),
        migrations.AddField(
            model_name='role',
            name='title',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='departmentschedule',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='department_schedules', to='companies.department'),
        ),
    ]
