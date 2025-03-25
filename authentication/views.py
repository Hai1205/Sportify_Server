from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from users.serializers import UserSerializer
from rest_framework.generics import GenericAPIView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from users.models import User
from .models import OTP
from Sportify_Server.services import *

class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                code = utils.generate_OTP()
                
                userData = UserSerializer(user).data
                
                OTP.objects.create(
                    user=user,
                    code=code,
                )
                
                recipient = userData["email"]
                mailService.mailActiveAccount(code, recipient)
                
                return JsonResponse({
                    "status": 200,
                    "message": "Register user successfully",
                }, safe=False, status=200)
            
            return JsonResponse({
                    "status": 400,
                    "message": "username or email already exists."
                }, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class CheckOTPView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, email):
        try:
            user = get_object_or_404(User, email=email)
            
            otp_code = request.data.get("OTP")

            if not otp_code:
                return JsonResponse({
                    "status": 400,
                    "message": "OTP is required!"
                }, status=400)

            otp_instance = OTP.objects.filter(user=user, code=otp_code).order_by('-timeExpired').first()

            if not otp_instance:                
                return JsonResponse({
                    "status": 400,
                    "message": "OTP is invalid!"
                }, status=400)

            if not otp_instance.is_valid():
                return JsonResponse({
                    "status": 400,
                    "message": "OTP is expired!"
                }, status=400)

            user.status = "active"
            user.save()
            
            otp_instance.delete()

            return JsonResponse({
                "status": 200,
                "message": "OTP is valid!",
            }, status=200)

        except Exception as e:
            print(e)
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class SendOTPView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, email):
        try:
            user = get_object_or_404(User, email=email)
            
            code = utils.generate_OTP()
            
            otp = OTP.objects.create(
                user=user,
                code=code,
            )
            from django.utils import timezone
            print("timeExpired " + str(otp.timeExpired))
            print("timezone.now() " + str(timezone.now()))
                
            recipient = user.email
            mailService.mailActiveAccount(code, recipient)

            return JsonResponse({
                "status": 200,
                "message": "OTP is sent!",
            }, status=200)

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

                if data.get("isPending"):
                    return JsonResponse({
                        "status": 202,
                        "message": data["message"],
                        "user": data["user"],
                        "isVerified": False,
                    }, status=202)

                response = JsonResponse({
                    "status": 200,
                    "message": "Login user successfully",
                    "user": data["user"],
                    "isVerified": True,
                }, status=200)

                # Lưu token vào cookies
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

            # Nếu có lỗi, kiểm tra user trước khi truy cập
            return JsonResponse({
                "status": 400,
                "message": "Username or password is incorrect.",
                "user": None,
                "isVerified": False,
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e),
                "isVerified": False,
            }, status=500)
            
class LoginWithGoogleView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginWithGoogleSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data

                response = JsonResponse({
                    "status": 200,
                    "message": "Login user successfully",
                    "user": data["user"],
                    "isVerified": True,
                }, status=200)

                # Lưu token vào cookies
                response.set_cookie(
                    key="access_token",
                    value=data["access_token"],
                    httponly=True,
                    secure=False,
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
                "message": "Invalid input data",
                "errors": serializer.errors,
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e),
                "isVerified": False,
            }, status=500)

class LogoutView(GenericAPIView):
    def post(self, request):
        try:
            response = JsonResponse({
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

            response = JsonResponse({
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
    def post(self, request):
        try:
            if request.user and (request.user.role == 'admin' or request.user.is_staff):
                return JsonResponse({
                    "status": 200,
                    "message": "You are admin",
                    "isAdmin": True
                }, safe=False, status=200)
            
            return JsonResponse({
                "status": 200,
                "message": "You are not admin",
                "isAdmin": False
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e),
                # "message": "You are not admin",
                "isAdmin": False
            }, status=500)
            
class CheckArtist(GenericAPIView):
    def post(self, request):
        try:
            if request.user and request.user.role == 'artist':
                return JsonResponse({
                    "status": 200,
                    "message": "You are artist",
                    "isAdmin": True
                }, safe=False, status=200)
            
            return JsonResponse({
                "status": 200,
                "message": "You are not artist",
                "isAdmin": False
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": "You are not artist",
                "isAdmin": False
            }, status=500)

class ChangePasswordView(GenericAPIView):
    def put(self, request, userId):
        try:
            serializer = ChangePasswordSerializer(userId, data=request.data)
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
            
class ForgotPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def put(self, request, userId):
        try:
            serializer = ForgotPasswordSerializer(userId, data=request.data)
            if serializer.is_valid():
                serializer.save()
                
                return JsonResponse({
                    "status": 200,
                    "message": "Forgot password successfully",
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
            
class ResetPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            
            password = utils.generate_password()
            email = user.email
            mailService.mailResetPassword(email, password)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)