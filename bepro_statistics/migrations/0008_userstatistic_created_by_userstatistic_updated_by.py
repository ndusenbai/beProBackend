# Generated by Django 4.0.5 on 2022-08-31 12:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bepro_statistics', '0007_alter_statisticobserver_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstatistic',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_stats_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userstatistic',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_stats_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
