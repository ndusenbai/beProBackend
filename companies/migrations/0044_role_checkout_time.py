# Generated by Django 4.0.5 on 2023-05-03 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0043_department_start_inaccuracy'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='checkout_time',
            field=models.PositiveIntegerField(default=15),
        ),
    ]
