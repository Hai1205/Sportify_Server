from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils.timezone import now

class User(AbstractUser):
    USER_ROLE_CHOICES = [
        ('user', 'User'),
        ('artist', 'Artist'),
        ('admin', 'Admin'),
    ]
    
    USER_STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('lock', 'lock'),
        ('active', 'Active'),
    ]
    
    COUNTRY_CHOICE = [
        ('vietnam', 'Vietnam'),
        ('usa', 'United States'),
        ('uk', 'United Kingdom'),
        ('france', 'France'),
        ('germany', 'Germany'),
        ('japan', 'Japan'),
        ('china', 'China'),
        ('south_korea', 'South Korea'),
        ('canada', 'Canada'),
        ('australia', 'Australia'),
        ('italy', 'Italy'),
        ('spain', 'Spain'),
        ('russia', 'Russia'),
        ('brazil', 'Brazil'),
        ('india', 'India'),
        ('mexico', 'Mexico'),
        ('netherlands', 'Netherlands'),
        ('switzerland', 'Switzerland'),
        ('sweden', 'Sweden'),
        ('singapore', 'Singapore'),
        ('uae', 'United Arab Emirates'),
        ('saudi_arabia', 'Saudi Arabia'),
        ('south_africa', 'South Africa')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, max_length=255, null=False, blank=False)
    email = models.EmailField(unique=True, max_length=255, null=False, blank=False)
    password = models.CharField(max_length=255, null=True, blank=False)
    fullName = models.CharField(max_length=255, null=False, blank=False, default=username)
    country = models.CharField(max_length=255, choices=COUNTRY_CHOICE, null=False, blank=False, default='vietnam')
    avatarUrl = models.URLField(default='avatar.com')
    status = models.CharField(max_length=10, choices=USER_STATUS_CHOICE, default='pending')
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='user')
   
    biography = models.CharField(max_length=1000, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    youtube = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    albums = models.ManyToManyField("albums.Album", related_name="albums_users")
    songs = models.ManyToManyField("songs.Song", related_name="songs_users")
    likedSongs = models.ManyToManyField("songs.Song", related_name="likedSongs_users")
    followers = models.ManyToManyField("self", blank=True, related_name='followers_users', symmetrical=False)
    following = models.ManyToManyField("self", blank=True, related_name='following_users', symmetrical=False)
    joinDate = models.DateField(default=now)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.id}, {self.role}, {self.is_staff}"


class ArtistApplication(models.Model):
    APPLICATION_STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('reject', 'Reject'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", null=False, blank=False, default=None, on_delete=models.CASCADE, related_name="user_artist_applications")
    songs = models.ManyToManyField("songs.Song", default=list, related_name="songs_applications")
    
    achievements = models.CharField(max_length=1000)
    reason = models.CharField(max_length=1000)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICE, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "artist_applications"

    def __str__(self):
        return f"ArtistApplication({self.id})"