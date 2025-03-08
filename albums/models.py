from django.db import models
from users.models import User
import uuid
from django.utils import timezone

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums", default=uuid.uuid4, db_column="userId")
    songs = models.JSONField(default=list)
    title = models.CharField(max_length=255, null=False, blank=False)
    releaseDate = models.DateField(default=timezone.now, null=False, blank=False)
    # description = models.CharField(max_length=255, null=False, blank=False)
    thumbnailUrl = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "albums"

    def __str__(self):
        return self.id