# Generated by Django 4.0.5 on 2022-09-05 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0034_alter_company_owner'),
        ('tests', '0003_test_job_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='companies.company'),
        ),
    ]