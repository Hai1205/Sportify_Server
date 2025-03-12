from django.db import models
import uuid

class Message:
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="messages", default=uuid.uuid4, db_column="sender_chats")
    receiver = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="messages", default=uuid.uuid4, db_column="receiver_chats")
    content = models.CharField(max_length=255, null=False, blank=True)

    class Meta:
        db_table = "messages"

    def __str__(self):
        return self.id

