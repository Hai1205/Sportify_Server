from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer, FullInfoUserSerializer
from django.shortcuts import get_object_or_404
from Sportify_Server.services import mailService, utils
from .models import OTP

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, data):
        password = data.pop("password")
        if len(password) < 8:
            raise serializers.ValidationError("Password is at least 8 characters.")
       
        user = User(
            **data,
            fullName=data['username']
        )
        user.set_password(password)
        user.is_staff = False
        user.save()
        
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            request = self.context.get('request')
            username = data.get("username")
            password = data.get("password")

            if "@" in username:
                user = get_object_or_404(User, email=username)
            else:
                user = get_object_or_404(User, username=username)

            if not user.check_password(password):
                raise serializers.ValidationError("Username or password is incorrect.")

            if user.status == 'lock':
                raise serializers.ValidationError("Account is lock.")

            if user.status == 'pending':
                code = utils.generate_OTP()
                OTP.objects.create(
                    user=user,
                    code=code,
                )
                
                recipient_email = user.email
                recipient_name = user.fullName
                sender_name = "Sportify"
                mailService.mailActiveAccount(code, recipient_name, sender_name, recipient_email)
                
                return {
                    "refresh_token": None,
                    "access_token": None,
                    "user": UserSerializer(user).data,
                    "isPending": True,
                    "message": "Account is pending verification. Please check your email for the OTP."
                }

            refresh = RefreshToken.for_user(user)
            return {
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "user": FullInfoUserSerializer(user).data,
            }
        except User.DoesNotExist:
            raise serializers.ValidationError("Username or password is incorrect.")

class LoginWithGoogleSerializer(serializers.Serializer):
    email = serializers.CharField()
    avatarUrl = serializers.CharField()
    fullName = serializers.CharField()

    def validate(self, data):
        email = data.get("email")

        user = User.objects.filter(email=email).first()
        if not user:
            username = email.split("@")[0]
            data['username'] = username
            user = self.create(data)

        refresh = RefreshToken.for_user(user)

        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
            "user": FullInfoUserSerializer(user).data,
        }
        
    def create(self, data):
        password = utils.generate_password()
        email = data.get("email")
        username = data.get("username", email)
       
        user = User(**data)
        user.set_password(password)
        user.username = username
        user.status = 'active'
        user.is_staff = False
        user.save()
        
        return user

class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)
    rePassword = serializers.CharField(write_only=True)

    def update(self, userId, data):
        user = get_object_or_404(User, id=userId)

        currentPassword = data["currentPassword"]
        if not user.check_password(currentPassword):
            raise serializers.ValidationError("Password is incorrect.")
        
        newPassword = data["newPassword"]
        rePassword = data["rePassword"]
        if newPassword != rePassword:
            raise serializers.ValidationError("Password does not match.")

        user.set_password(newPassword)
        user.save()
        
        return user
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)
    rePassword = serializers.CharField(write_only=True)

    def update(self, data):
        email = data["email"]
        user = get_object_or_404(User, email=email)

        newPassword = data["newPassword"]
        rePassword = data["rePassword"]
        if newPassword != rePassword:
            raise serializers.ValidationError("Password does not match.")

        user.set_password(newPassword)
        user.save()
        
        return user