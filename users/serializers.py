from rest_framework import serializers
from .models import User, ArtistApplication
from albums.serializers import AlbumSerializer
from songs.serializers import SongSerializer

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
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('fullName', 'username', 'email', 'is_staff', "role", "status")
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, data):
        password = data.pop("password")
        
        if data.get("role") == "admin":
            data["is_staff"] = True
            
        user = User(**data)
        user.set_password(password)
        user.save()
      
        return user 

# class UpdateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'fullName', 'country', 'avatarUrl', 'status', 'role', 'biography']
#         # extra_kwargs = {'password': {'write_only': True}}

#     def update(self, user, validated_data):
#         password = validated_data.pop("password", None)  # Lấy password nếu có
#         if password:
#             user.set_password(password)  # Mã hóa password
        
#         fullName = validated_data.pop("fullName", None)  # Lấy fullName nếu có
#         if fullName:
#             user.fullName = fullName
        
#         user.save()  # Lưu user vào database
        
#         return user
    
class ResponseUpdateUserToArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistApplication
        fields = ['id', 'status']

    def update(self, application, data):
        status = data.get("status")
        
        application.status = status
        
        if status == "approved":
            application.user.role = "artist"
            application.user.save()
        
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