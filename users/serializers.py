from rest_framework import serializers
from .models import User
from albums.serializers import AlbumSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class FullInfoUserSerializer(serializers.ModelSerializer):
    albums = AlbumSerializer(many=True, read_only=True)
    followers = UserSerializer(many=True, read_only=True)
    following = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'fullName']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, user, validated_data):
        password = validated_data.pop("password", None)  # Lấy password nếu có
        if password:
            user.set_password(password)  # Mã hóa password
        
        fullName = validated_data.pop("fullName", None)  # Lấy fullName nếu có
        if fullName:
            user.fullName = fullName
        
        user.save()  # Lưu user vào database
        
        return user
    
class ResponseUpdateUserToArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'status', 'role']

    def update(self, user, data):
        role = data.get("role")
        
        user.status = "active"
        user.role = role
        
        user.save()  # Lưu user vào database
        
        return user

class RequireUpdateUserToArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']

    def update(self, user, data):
        user.status = "pending"
        
        user.save()  # Lưu user vào database
        
        return user
