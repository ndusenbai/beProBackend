# Generated by Django 4.0.5 on 2022-07-20 05:01

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0007_alter_user_assistant_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcceptCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.PositiveIntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(9999)])),
                ('expiration', models.DateTimeField(blank=True, editable=False)),
                ('is_accepted', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pin_codes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Код для восстановления пароля',
                'verbose_name_plural': 'Коды для восстановления пароля',
                'ordering': ['-created_at'],
            },
        ),
    ]
