from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone

class OTP(models.Model):
    timeExpired = timezone.now() + timedelta(minutes=5)
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_otps", default=None)
    code = models.CharField(max_length=6, null=False, blank=True)
    codeExpired = models.DateTimeField(default=timeExpired)

    class Meta:
        db_table = "otps"

    def __str__(self):
        return self.id

    def is_valid(self):
        # print("timezone.now() " + str(timezone.now()))
        # print("self.codeExpired " + str(self.codeExpired))
        return timezone.now() < self.codeExpired
