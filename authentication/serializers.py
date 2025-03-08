from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer

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
        username = data.get("username")
        password = data.get("password")

        # Kiểm tra xem người dùng có tồn tại không
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Sai tên đăng nhập hoặc mật khẩu.")

        # Kiểm tra mật khẩu
        if not user.check_password(password):
            raise serializers.ValidationError("Sai tên đăng nhập hoặc mật khẩu.")

        if not user.is_active:
            raise serializers.ValidationError("Tài khoản này đã bị vô hiệu hóa.")

        # Tạo token JWT
        refresh = RefreshToken.for_user(user)
        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }
