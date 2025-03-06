from django.db import models
import uuid

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=255, null=False, blank=False)
    thumbnail_id = models.UUIDField(default=uuid.uuid4)
    thumbnailUrl = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "albums"

    def __str__(self):
        return self.id