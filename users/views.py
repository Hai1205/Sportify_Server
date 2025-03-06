from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import UserSerializer, UpdateUserSerializer
from .models import CustomUser
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404

class GetAllUserView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
       
        return Response(serializer.data)

class GetUserByIdView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userId):
        user = get_object_or_404(CustomUser, id=userId)
        serializer = UserSerializer(user)
       
        return Response(serializer.data)
    
class UpdateUserByIdView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, userId):
        user = get_object_or_404(CustomUser, id=userId)
        serializer = UpdateUserSerializer(user, data=request.data)
       
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteUserByIdView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, userId):
        user = get_object_or_404(CustomUser, id=userId)
        user.delete()
       
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class GetSongByIdView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, userId):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
       
        return Response(serializer.data)