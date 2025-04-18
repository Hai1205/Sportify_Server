# Generated by Django 5.1.6 on 2025-03-27 16:36

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('songs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('releaseDate', models.DateField(default=django.utils.timezone.now)),
                ('thumbnailUrl', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('songs', models.ManyToManyField(blank=True, related_name='songs_albums', to='songs.song')),
            ],
            options={
                'db_table': 'albums',
            },
        ),
    ]
