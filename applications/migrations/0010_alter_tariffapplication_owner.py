# Generated by Django 4.0.5 on 2022-06-24 04:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applications', '0009_alter_tariffapplication_tariff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tariffapplication',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tariff_applications', to=settings.AUTH_USER_MODEL),
        ),
    ]
