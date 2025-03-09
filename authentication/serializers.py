from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer
from django.shortcuts import get_object_or_404

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ('id', 'username', 'email', 'password')
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop("password")  # Lấy password ra khỏi validated_data
        user = User(**validated_data)  # Tạo user nhưng chưa có password
        user.set_password(password)  # Mã hóa password
        user.is_staff = False  # Chặn client tự cấp quyền admin
        user.save()  # Lưu user vào database
        
        return user
    
class RegisterAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ('id', 'username', 'email', 'password', 'is_staff')
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
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
