from rest_framework import serializers
from .models import User, ArtistApplication
from albums.serializers import AlbumSerializer
from songs.serializers import SongSerializer, FullInfoSongSerializer
from Sportify_Server.services import mailService

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class FullInfoUserSerializer(serializers.ModelSerializer):
    albums = AlbumSerializer(many=True, read_only=True)
    followers = UserSerializer(many=True, read_only=True)
    following = UserSerializer(many=True, read_only=True)
    songs = FullInfoSongSerializer(many=True, read_only=True)
    likedSongs = SongSerializer(many=True, read_only=True)
    likedAlbums = AlbumSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('fullName', 'password', 'username', 'email', 'is_staff', "role", "status")

    def create(self, data):
        password = data.pop("password")
        
        if data.get("role") == "admin":
            data["is_staff"] = True
            
        user = User(**data)
        user.set_password(password)
        user.save()
      
        return user 

class ResponseUpdateUserToArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistApplication
        fields = ['id', 'status', 'rejectionReason', 'details']

    def update(self, application, data):
        # request = self.context.get('request')
        status = data.get("status") 
        details = data.get("details")
        rejectionReason = data.get("rejectionReason")
        
        application.status = status
        application.details = details
        application.rejectionReason = rejectionReason
        
        if status == "approve":
            application.user.role = "artist"
            application.user.save()
            
            recipient_email = application.user.email
            recipient_name = application.user.fullName
            sender_name = "Sportify"
            mailService.mailApproveArtist(recipient_name, sender_name, recipient_email, details)
            
        if status == "reject":
            
            application.user.role = "user"
            application.user.save()
            
            recipient_email = application.user.email
            recipient_name = application.user.fullName
            sender_name = "Sportify"
            mailService.mailRejectArtist(recipient_name, sender_name, recipient_email, details, rejectionReason)
        
        application.save()
        return application

class ArtistApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistApplication
        fields = '__all__'

class FullInfoArtistApplicationSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ArtistApplication
        fields = '__all__'