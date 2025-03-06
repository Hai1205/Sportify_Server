from django.db import models
from albums.models import Album
import uuid

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False, blank=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="songs")
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=255, null=False, blank=False)
    singer = models.CharField(max_length=255, null=False, blank=False)
    thumbnailUrl = models.URLField()
    audioUrl = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "songs"

    def __str__(self):
        return self.id