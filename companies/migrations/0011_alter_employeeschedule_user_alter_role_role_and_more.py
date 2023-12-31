# Generated by Django 4.0.5 on 2022-06-20 07:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0010_role_grade_role_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeschedule',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_schedules', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.IntegerField(choices=[(1, 'Owner'), (2, 'HR'), (3, 'Observer'), (4, 'Employee')], default=4, max_length=50),
        ),
        migrations.AlterField(
            model_name='role',
            name='title',
            field=models.CharField(default='', max_length=200),
        ),
    ]
