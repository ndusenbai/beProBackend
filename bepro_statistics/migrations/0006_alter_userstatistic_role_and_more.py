# Generated by Django 4.0.5 on 2022-07-13 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0030_alter_role_user'),
        ('bepro_statistics', '0005_remove_statistic_user_remove_statisticobserver_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstatistic',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.role'),
        ),
        migrations.AlterField(
            model_name='userstatistic',
            name='statistic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bepro_statistics.statistic'),
        ),
        migrations.AddConstraint(
            model_name='userstatistic',
            constraint=models.UniqueConstraint(fields=('statistic', 'role', 'day'), name='unique stat-role-day'),
        ),
    ]
