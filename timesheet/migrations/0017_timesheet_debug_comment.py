# Generated by Django 4.0.5 on 2022-09-02 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0016_alter_employeeschedule_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheet',
            name='debug_comment',
            field=models.TextField(blank=True),
        ),
    ]