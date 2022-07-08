# Generated by Django 4.0.5 on 2022-07-08 04:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0028_company_is_deleted'),
        ('scores', '0002_alter_reason_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='score',
            name='user',
        ),
        migrations.AddField(
            model_name='score',
            name='role',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='companies.role'),
            preserve_default=False,
        ),
    ]
