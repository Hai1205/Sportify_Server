from django.db import models
from users.models import User
import uuid

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False, blank=False)
    user = models.ForeignKey("users.User", default=uuid.uuid4, on_delete=models.CASCADE, related_name="user_songs")
    album = models.ForeignKey("albums.Album", default=uuid.uuid4, on_delete=models.CASCADE, related_name="album_songs")
    title = models.CharField(max_length=255, null=False, blank=False)
    thumbnailUrl = models.URLField()
    audioUrl = models.URLField()
    duration = models.IntegerField(null=False, blank=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "songs"

    def __str__(self):
        return self.id