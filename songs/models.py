from django.db import models
from albums.models import Album
from users.models import User
import uuid

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False, blank=False)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="songs", db_column="userId")
    albumId = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="album_songs", db_column="albumId")
    title = models.CharField(max_length=255, null=False, blank=False)
    thumbnailUrl = models.URLField()
    audioUrl = models.URLField()
    duration = models.IntegerField(null=False, blank=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    # description = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        db_table = "songs"

    def __str__(self):
        return self.id