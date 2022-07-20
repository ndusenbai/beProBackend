# Generated by Django 4.0.5 on 2022-07-20 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0008_acceptcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='acceptcode',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='acceptcode',
            unique_together={('code', 'is_accepted')},
        ),
    ]
