from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer
from django.shortcuts import get_object_or_404

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('fullName', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, data):
        password = data.pop("password")  # Lấy password ra khỏi data
        user = User(**data)  # Tạo user nhưng chưa có password
        user.set_password(password)  # Mã hóa password
        user.is_staff = False  # Chặn client tự cấp quyền admin
        user.save()  # Lưu user vào database
        
        return user
    
class RegisterAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('fullName', 'username', 'email', 'password', 'is_staff')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, data):
        password = data.pop("password")
        user = User(**data)
        user.is_staff = True
        user.set_password(password)
        user.save()
      
        return user  
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            username = data.get("username")
            password = data.get("password")
            
            if "@" in username:
                user = get_object_or_404(User, email=username)
            else:
                user = get_object_or_404(User, username=username)
           
            # Kiểm tra mật khẩu
            if not user.check_password(password):
                raise serializers.ValidationError("Username or password is incorrect.")

            if user.status == 'locked':
                raise serializers.ValidationError("Account is locked.")

            # Tạo token JWT
            refresh = RefreshToken.for_user(user)
            return {
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "user": UserSerializer(user).data,
            }
        except User.DoesNotExist:
            raise serializers.ValidationError("Username or password is incorrect.")

class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)
    rePassword = serializers.CharField(write_only=True)

    def update(self, userId, data):
        user = get_object_or_404(User, id=userId)

        currentPassword = data["currentPassword"]
        newPassword = data["newPassword"]
        rePassword = data["rePassword"]

        if not user.check_password(currentPassword):
            raise serializers.ValidationError("Password is incorrect.")
        
        if newPassword != rePassword:
            raise serializers.ValidationError("Password does not match.")

        user.set_password(newPassword)  # Mã hóa mật khẩu mới
        user.save()  # Lưu vào database
        
        return user