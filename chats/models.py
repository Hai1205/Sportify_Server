from django.db import models
from users.models import User
import uuid

class Message:
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    senderId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages", default=uuid.uuid4, db_column="senderId")
    receiverId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages", default=uuid.uuid4, db_column="receiverId")
    content = models.CharField(max_length=255, null=False, blank=True)

    class Meta:
        db_table = "messages"

    def __str__(self):
        return self.id

