# Generated by Django 4.0.5 on 2022-07-13 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scores', '0004_score_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='created_at',
            field=models.DateField(),
        ),
    ]