from rest_framework.generics import GenericAPIView
from django.http import JsonResponse
from django.db.models import Q
from .models import Message
from users.models import User
from .serializers import MessageSerializer
from django.shortcuts import get_object_or_404

class GetAllMessageView(GenericAPIView):
    def get(self, request):
        try:
            messages = Message.objects.all()
            serializer = MessageSerializer(messages, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Get all message successfully",
                "Messages": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class getMessageView(GenericAPIView):
    def get(self, request, senderId, receiverId):
        try:
            get_object_or_404(User, senderId)
            get_object_or_404(User, receiverId)
            
            messages = Message.objects.filter(
                Q(senderId=senderId, receiverId=receiverId) | Q(senderId=receiverId, receiverId=senderId)
            ).order_by("created_at")

            serializer = MessageSerializer(messages, many=True)
            
            return JsonResponse({
                "status": 200,
                "message": "Get message successfully",
                "Message": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
