from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from Sportify_Server.permissions import IsArtistUser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, \
                            RegisterSerializer, \
                            RegisterAdminSerializer, \
                            ChangePasswordSerializer
from users.serializers import UserSerializer
from rest_framework.generics import GenericAPIView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from users.models import User

class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                userSerializer = UserSerializer(user)
                
                return JsonResponse({
                    "status": 200,
                    "message": "Register user successfully",
                    "user": userSerializer.data
                }, safe=False, status=200)
            
            return JsonResponse({
                    "status": 400,
                    "message": str(serializer.errors)
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class RegisterAdminView(GenericAPIView):
    permission_classes = [IsAdminUser] 
    # permission_classes = [] 

    def post(self, request):
        
        try:
            serializer = RegisterAdminSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                userSerializer = UserSerializer(user)
                
                return Response({
                    "status": 200,
                    "message": "Register admin successfully",
                    "user": userSerializer.data
                }, status=200)
            
            return JsonResponse({
                    "status": 400,
                    "message": str(serializer.errors)
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class LoginView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                
                response = Response({
                    "status": 200,
                    "message": "Login user successfully",
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
            
            return JsonResponse({
                    "status": 400,
                    "message": str(serializer.errors)
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

    
class LogoutView(GenericAPIView):
    def post(self, request):
        try:
            response = Response({
                "status": 200,
                "message": "Logout user successfully"
            }, status=200)

            # Xóa token khỏi cookies
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')

            return response
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class TokenRefreshView(GenericAPIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if not refresh_token:
                return JsonResponse({
                    "status": 403,
                    "message": "Refresh token not found"
                    }, status=403)

            refresh = RefreshToken(refresh_token)
            
            access_token = str(refresh.access_token)

            response = Response({
                "status": 200,
                "message": "Access token has been refresh"
            }, status=200)
            
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax"
            )

            return response
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class CheckAdmin(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        try:
            return JsonResponse({
                "status": 200,
                "message": "You are admin",
                "isAdmin": True
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "You are not admin",
                "isAdmin": False
            }, status=500)
            
class CheckArtist(GenericAPIView):
    permission_classes = [IsArtistUser]
    
    def post(self, request):
        try:
            return JsonResponse({
                "status": 200,
                "message": "You are artist",
                "isArtist": True
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "You are not artist",
                "isArtist": False
            }, status=500)

class ChangePasswordView(GenericAPIView):
    def put(self, request, userId):
        try:
            print(1)
            serializer = ChangePasswordSerializer(userId, data=request.data)
            print(2)
            if serializer.is_valid():
                serializer.save()
                
                return JsonResponse({
                    "status": 200,
                    "message": "Changed password successfully",
                }, safe=False, status=200)
            
            return JsonResponse({
                "status": 400,
                "message": serializer.errors
            }, safe=False, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)