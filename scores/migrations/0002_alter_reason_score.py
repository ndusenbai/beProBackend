# Generated by Django 4.0.5 on 2022-06-17 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scores', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reason',
            name='score',
            field=models.SmallIntegerField(),
        ),
    ]
