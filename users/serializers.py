from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, user, validated_data):
        password = validated_data.pop("password", None)  # Lấy password nếu có
        if password:
            user.set_password(password)  # Mã hóa password
        
        user.save()  # Lưu user vào database
        
        return user