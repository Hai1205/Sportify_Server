from rest_framework.generics import GenericAPIView
from django.http import JsonResponse
from django.db.models import Q
from .models import Message
from users.models import User
from .serializers import MessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.db.models import Q, Max, Prefetch
import logging

logger = logging.getLogger(__name__)

class GetAllMessageView(GenericAPIView):
    def get(self, request):
        try:
            messages = Message.objects.all()
            serializer = MessageSerializer(messages, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Get all message successfully",
                "messages": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class getMessageView(GenericAPIView):
    def get(self, request, senderId, receiverId):
        try:
            # Lấy thông số phân trang từ request
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 20))
            
            offset = (page - 1) * limit
            
            sender = get_object_or_404(User, id=senderId)
            receiver = get_object_or_404(User, id=receiverId)

            # Lấy tổng số tin nhắn
            total_count = Message.objects.filter(
                Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
            ).count()
            
            # Query với phân trang và sắp xếp từ mới đến cũ
            messages = Message.objects.filter(
                Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
            ).order_by("-created_at")[offset:offset + limit]
            
            # Đảo ngược danh sách để khi hiển thị tin nhắn cũ nằm trên, mới nằm dưới
            messages = list(reversed(messages))
            
            serializer = MessageSerializer(messages, many=True)
            
            # Trả về metadata phân trang
            has_more = (offset + limit) < total_count
            
            return JsonResponse({
                "status": 200,
                "message": "Get message successfully",
                "messages": serializer.data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "hasMore": has_more
                }
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class ChatRoomListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        rooms = ChatRoom.objects.filter(members=user)
        
        # Prefetch members để tránh N+1 query
        rooms = rooms.prefetch_related('members')
        
        # Lấy tin nhắn mới nhất cho mỗi room
        rooms = rooms.annotate(
            last_message_time=Max('messages__created_at')
        ).order_by('-last_message_time')
        
        serializer = ChatRoomSerializer(rooms, many=True, context={'user': user})
        return Response({'rooms': serializer.data})

class ChatRoomMessagesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id, members=request.user)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found or you are not a member'}, status=status.HTTP_404_NOT_FOUND)
        
        messages = Message.objects.filter(chat_room=room).order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response({'messages': serializer.data})

class CreateGroupChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        name = request.data.get('name')
        member_ids = request.data.get('member_ids', [])
        
        if not name or not member_ids:
            return Response({'error': 'Name and member_ids are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Thêm người tạo vào danh sách thành viên
        if str(request.user.id) not in member_ids:
            member_ids.append(str(request.user.id))
        
        try:
            room = ChatRoom.objects.create(name=name, room_type='group')
            for member_id in member_ids:
                room.members.add(member_id)
            
            serializer = ChatRoomSerializer(room, context={'user': request.user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StartDirectChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        recipient_id = request.data.get('recipient_id')
        
        if not recipient_id:
            return Response({'error': 'Recipient ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sender = request.user
            recipient = User.objects.get(id=recipient_id)
            
            # Tìm hoặc tạo phòng chat trực tiếp
            room = ChatRoom.get_or_create_direct_room(sender, recipient)
            
            serializer = ChatRoomSerializer(room, context={'user': request.user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetMessageView(APIView):
    def get(self, request, my_id, opponent_id):
        try:
            # Kiểm tra cả hai user có tồn tại không
            try:
                user1 = User.objects.get(id=my_id)
                user2 = User.objects.get(id=opponent_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "One or both users do not exist"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Lấy hoặc tạo phòng chat giữa hai người
            chat_room = ChatRoom.get_or_create_direct_room(user1, user2)
            
            # Lấy tin nhắn từ phòng chat này
            messages = Message.objects.filter(
                chat_room=chat_room
            ).order_by('created_at')
            
            serialized_messages = MessageSerializer(messages, many=True).data
            logger.info(f"Retrieved {len(serialized_messages)} messages between {my_id} and {opponent_id}")
            
            return Response(serialized_messages, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving messages: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
