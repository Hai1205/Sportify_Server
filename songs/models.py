from django.db import models
import uuid
from Sportify_Server.mixin import GenreMixin
from django.utils.timezone import now
 
class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False, blank=False)
    user = models.ForeignKey("users.User", null=False, blank=False, default=None, on_delete=models.CASCADE, related_name="user_songs")
    album = models.ForeignKey("albums.Album", null=True, blank=True, default=None, on_delete=models.CASCADE, related_name="album_songs")
    
    title = models.CharField(max_length=255, null=False, blank=False)
    genre = models.CharField(max_length=255, validators=[GenreMixin.validate_genres], null=False, blank=False)
    releaseDate = models.DateField(default=now, null=False, blank=False)
    # songwriter = models.CharField(max_length=255, null=False, blank=False)
    # producer = models.CharField(max_length=255, null=False, blank=False)
    
    thumbnailUrl = models.URLField()
    audioUrl = models.URLField()
    
    lyric = models.CharField(max_length=8000, null=False, blank=False, default="")
    duration = models.IntegerField(null=False, blank=False, default=0)
    views = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "songs"

    def __str__(self):
        return self.id