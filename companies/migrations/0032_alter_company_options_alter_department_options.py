# Generated by Django 4.0.5 on 2022-07-18 06:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0031_remove_role_unique company-user_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ('id',), 'verbose_name_plural': 'Companies'},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ('id',)},
        ),
    ]