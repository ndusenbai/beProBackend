# Generated by Django 4.0.5 on 2022-06-22 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bepro_statistics', '0002_remove_statistic_company_alter_statistic_plan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='statistic_type',
            field=models.IntegerField(choices=[(1, 'General statistics'), (2, 'Double statistics'), (3, 'Inverted statistics')], default=1),
        ),
    ]