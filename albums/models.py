from django.db import models
import uuid
from django.utils import timezone
from Sportify_Server.mixin import GenreMixin

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    songs = models.ManyToManyField("songs.Song", blank=True, related_name='songs_albums')
    title = models.CharField(max_length=255, null=False, blank=False)
    genre = models.CharField(max_length=255, null=False, blank=False, validators=[GenreMixin.validate_genres])
    releaseDate = models.DateField(default=timezone.now, null=False, blank=False)
    thumbnailUrl = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "albums"

    def __str__(self):
        return self.id