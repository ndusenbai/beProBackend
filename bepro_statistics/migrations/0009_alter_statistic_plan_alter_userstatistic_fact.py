# Generated by Django 4.0.5 on 2022-10-27 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bepro_statistics', '0008_userstatistic_created_by_userstatistic_updated_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='plan',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userstatistic',
            name='fact',
            field=models.IntegerField(),
        ),
    ]
