from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, RegisterSerializer, RegisterAdminSerializer
from users.serializers import UserSerializer
from rest_framework.generics import GenericAPIView
from django.http import JsonResponse

class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                return JsonResponse({
                    "message": "Register successfully",
                    "user": UserSerializer(user).data
                }, status=200)
            
            return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class RegisterAdminView(GenericAPIView):
    permission_classes = [IsAdminUser] 

    def post(self, request):
        try:
            serializer = RegisterAdminSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                return Response({
                    "message": "Register admin successfully",
                    "user": UserSerializer(user).data
                }, status=200)
            
            return Response(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class LoginView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                
                response = Response({
                    "message": "Login successfully",
                    "user": data["user"]
                }, status=200)

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
            
            return Response(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    
class LogoutView(GenericAPIView):
    def post(self, request):
        try:
            response = Response({
                "message": "Logged out successfully"
            }, status=200)

            # Xóa token khỏi cookies
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')

            return response
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class TokenRefreshView(GenericAPIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if not refresh_token:
                return Response({"error": "Refresh token not found"}, status=403)

            refresh = RefreshToken(refresh_token)
            
            access_token = str(refresh.access_token)

            response = Response({"message": "Access token has been refresh"}, status=200)
            
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax"
            )

            return response
        except Exception:
            return Response({"error": "Refresh token is invalid"}, status=403)
    
class CheckAdmin(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        try:
            return JsonResponse({
                "isAdmin": True
            }, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)