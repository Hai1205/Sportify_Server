from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone

# Hàm tạo giá trị mặc định cho timeExpired
def default_expiry():
    return timezone.now() + timedelta(minutes=5)

class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_otps", default=None)
    code = models.CharField(max_length=6, null=False, blank=True)
    timeExpired = models.DateTimeField(default=default_expiry)  # Dùng hàm có tên thay vì lambda
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otps"

    def __str__(self):
        return str(self.id)

    def is_valid(self):
        # print("timezone.now():", timezone.now())
        # print("self.timeExpired:", self.timeExpired)
        return timezone.now() < self.timeExpired
