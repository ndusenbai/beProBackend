# Generated by Django 4.0.5 on 2022-06-15 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0004_alter_applicationtocreatecompany_employees_qty_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationtocreatecompany',
            name='company_legal_name',
            field=models.CharField(max_length=200),
        ),
    ]
