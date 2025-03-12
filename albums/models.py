from django.db import models
# from songs.models import Song
import uuid
from django.utils import timezone
# from users.models import User

class Album(models.Model):
            
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", default=uuid.uuid4, on_delete=models.CASCADE, related_name="user_albums")
    songs = models.ManyToManyField("songs.Song", blank=True, related_name='songs_albums')
    title = models.CharField(max_length=255, null=False, blank=False)
    releaseDate = models.DateField(default=timezone.now, null=False, blank=False)
    thumbnailUrl = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "albums"

    def __str__(self):
        return self.id