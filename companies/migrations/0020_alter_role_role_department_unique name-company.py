# Generated by Django 4.0.5 on 2022-06-22 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0019_department_head_of_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.IntegerField(choices=[(1, 'Owner'), (2, 'HR'), (3, 'Observer'), (4, 'Employee'), (5, 'Head of department')], default=4),
        ),
        migrations.AddConstraint(
            model_name='department',
            constraint=models.UniqueConstraint(fields=('name', 'company'), name='unique name-company'),
        ),
    ]
