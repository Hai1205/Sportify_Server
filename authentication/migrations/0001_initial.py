# Generated by Django 5.1.6 on 2025-03-20 04:50

import authentication.models
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(blank=True, max_length=6)),
                ('timeExpired', models.DateTimeField(default=authentication.models.default_expiry)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='user_otps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'otps',
            },
        ),
    ]
