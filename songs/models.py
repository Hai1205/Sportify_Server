from django.db import models
import uuid
from django.utils import timezone
 
class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False, blank=False)

    title = models.CharField(max_length=255, null=False, blank=False)
    releaseDate = models.DateField(default=timezone.now)

    thumbnailUrl = models.URLField()
    audioUrl = models.URLField()
    videoUrl = models.URLField()

    lyrics = models.CharField(max_length=8000, null=False, blank=False, default="")
    duration = models.IntegerField(null=False, blank=False, default=0)
    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "songs"

    def __str__(self):
        return str(self.id)
