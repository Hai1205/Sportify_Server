from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, RegisterSerializer, RegisterAdminSerializer
from users.serializers import UserSerializer
from rest_framework.generics import GenericAPIView

class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                "message": "Register successfully",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAdminView(GenericAPIView):
    permission_classes = [IsAdminUser]  # Chỉ admin mới gọi API này

    def post(self, request):
        serializer = RegisterAdminSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                "message": "Register admin successfully",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            response = Response({
                "message": "Login successfully",
                "user": data["user"]
            }, status=status.HTTP_200_OK)

            # Lưu token vào cookies với HttpOnly
            response.set_cookie(
                key="access_token",
                value=data["access_token"],
                httponly=True,
                secure=False,  # Đặt thành False nếu không dùng HTTPS
                samesite="Lax"
            )
            
            response.set_cookie(
                key="refresh_token",
                value=data["refresh_token"],
                httponly=True,
                secure=False,
                samesite="Lax"
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(GenericAPIView):
    def post(self, request):
        response = Response({
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)

        # Xóa token khỏi cookies
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')

        return response

class TokenRefreshView(GenericAPIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token not found"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            
            access_token = str(refresh.access_token)
        except Exception:
            return Response({"error": "Refresh token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({"message": "Access token has been refresh"}, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        return response