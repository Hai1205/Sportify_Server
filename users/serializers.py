from rest_framework import serializers
from .models import User
class UserSerializer(serializers.ModelSerializer):
    albums = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        # fields = ['id', 'username', 'email', 'fullName', 'avatarUrl', 'role', 'created_at']
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password']
        # fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, user, validated_data):
        password = validated_data.pop("password", None)  # Lấy password nếu có
        if password:
            user.set_password(password)  # Mã hóa password
        
        user.save()  # Lưu user vào database
        
        return user
    
class ResponseUpdateUserToArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'status', 'role']
        # fields = '__all__'
        # extra_kwargs = {'password': {'write_only': True}}

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
        # fields = '__all__'
        # extra_kwargs = {'password': {'write_only': True}}

    def update(self, user, data):
        user.status = "pending"
        
        user.save()  # Lưu user vào database
        
        return user

class UserWithSongsSerializer(serializers.ModelSerializer):
    # from albums.serializers import AlbumSerializer
    # albums = AlbumSerializer(many=True, read_only=True)
    albums = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        # fields = ['id', 'role']
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
