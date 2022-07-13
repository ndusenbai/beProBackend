# Generated by Django 4.0.5 on 2022-07-13 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0029_alter_role_options'),
        ('bepro_statistics', '0004_rename_weekday_userstatistic_day'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistic',
            name='user',
        ),
        migrations.RemoveField(
            model_name='statisticobserver',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userstatistic',
            name='user',
        ),
        migrations.AddField(
            model_name='statistic',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='companies.role'),
        ),
        migrations.AddField(
            model_name='statisticobserver',
            name='role',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='observing_statistics', to='companies.role'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userstatistic',
            name='role',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_statistics', to='companies.role'),
            preserve_default=False,
        ),
    ]