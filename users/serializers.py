from rest_framework import serializers
from .models import User, ArtistApplication
from albums.serializers import AlbumSerializer
from songs.serializers import SongSerializer
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
    songs = SongSerializer(many=True, read_only=True)
    likedSongs = SongSerializer(many=True, read_only=True)
    
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
        request = self.context.get('request')
        status = data.get("status")
        rejectionReason = data.get("rejectionReason")
        details = data.get("details")
        
        application.status = status
        
        if status == "approve":
            application.user.role = "artist"
            application.details = details
            application.user.save()
            
            recipient_email = application.user.email
            recipient_name = application.user.fullName
            sender_name = request.user.fullName
            mailService.mailApproveArtist(recipient_name, sender_name, recipient_email, details)
            
        if status == "reject":
            application.rejectionReason = rejectionReason
            application.details = details
            application.user.save()
            
            recipient_email = application.user.email
            recipient_name = application.user.fullName
            sender_name = request.user.fullName
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