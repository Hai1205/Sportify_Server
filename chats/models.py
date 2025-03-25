from django.db import models
from django.utils import timezone
import uuid

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="sender_messages", db_column="sender")
    receiver = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="receiver_messages", db_column="receiver")
    content = models.CharField(max_length=255, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"

    def __str__(self):
        return str(self.id)
