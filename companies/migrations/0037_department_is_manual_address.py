# Generated by Django 4.0.5 on 2022-09-16 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0036_alter_department_head_of_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='is_manual_address',
            field=models.BooleanField(default=False),
        ),
    ]
