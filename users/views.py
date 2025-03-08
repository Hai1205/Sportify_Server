from rest_framework.permissions import IsAdminUser
from .serializers import UserSerializer, UpdateUserSerializer, UpdateUserToArtistSerializer, UserWithSongsSerializer
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
        
            return JsonResponse(serializer.data, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class GetUserView(GenericAPIView):
    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = UserSerializer(user)
        
            return JsonResponse(serializer.data, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class UpdateUserView(GenericAPIView):
    def put(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = UpdateUserSerializer(user, data=request.data)
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse(serializer.data, status=200)
            
            return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class DeleteUserView(GenericAPIView):
    def delete(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            user.delete()
        
            return JsonResponse({"message": "Deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class GetUserSongView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = UserWithSongsSerializer(user, many=True)
        
            return JsonResponse(serializer.data, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class UpdateUserToArtistView(GenericAPIView):
    def put(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = UpdateUserToArtistSerializer(user)
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse(serializer.data, status=200)
            
            return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)