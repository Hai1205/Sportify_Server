from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
# from albums.models import Album

class User(AbstractUser):
    USER_ROLE_CHOICES = [
        ('user', 'User'),
        ('artist', 'Artist'),
        ('admin', 'Admin'),
    ]
    
    USER_STATUS = [
        ('pending', 'Pending'),
        ('locked', 'Locked'),
        ('active', 'Active'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, max_length=10, null=False, blank=False)
    email = models.EmailField(unique=True, max_length=255, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    fullName = models.CharField(max_length=255, null=False, blank=False, default=username)
    avatarUrl = models.URLField(default='avatar.com')
    albums = models.ManyToManyField("albums.Album", default=uuid.uuid4, related_name="albums_users")
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='user')
    status = models.CharField(max_length=10, choices=USER_STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.id} ({self.role})"
