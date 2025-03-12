from rest_framework.permissions import IsAdminUser
from .serializers import UserSerializer, UpdateUserSerializer, ResponseUpdateUserToArtistSerializer, UserWithSongsSerializer, RequireUpdateUserToArtistSerializer
from .models import User
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

class GetAllUserView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Get all user successfully",
                "users": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class GetUserView(GenericAPIView):
    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = UserSerializer(user)
        
            return JsonResponse({
                "status": 200,
                "message": "Get user successfully",
                "user": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class UpdateUserView(GenericAPIView):
    def put(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = UpdateUserSerializer(user, data=request.data)
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse({
                    "status": 200,
                    "message": "Updated user successfully",
                    "users": serializer.data
                }, safe=False, status=200)
            
            return JsonResponse({
                "status": 400,
                "message": {serializer.errors}
            }, safe=False, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class DeleteUserView(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def delete(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            user.delete()
        
            return JsonResponse({
                    "status": 200,
                    "message": "Deleted user successfully",
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class getAllUsersongView(GenericAPIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = UserWithSongsSerializer(user, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Updated user successfully",
                "user": serializer.data
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class RequireUpdateUserToArtistView(GenericAPIView):
    def put(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = RequireUpdateUserToArtistSerializer(user, data=request.data)
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse({
                    "status": 200,
                    "message": "Required update user to artist successfully",
                    # "user": serializer.data
                }, status=200)
            
            return JsonResponse({
                "status": 400,
                "message": {serializer.errors}
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
        
class ResponseUpdateUserToArtistView(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def put(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = ResponseUpdateUserToArtistSerializer(user, data=request.data)
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse({
                    "status": 200,
                    "message": "Responsed update user to artist successfully",
                    # "user": serializer.data
                }, status=200)
            
            return JsonResponse({
                "status": 400,
                "message": {serializer.errors}
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)