from django.db import models
from django.utils import timezone
import uuid
from users.models import User

class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROOM_TYPES = (
        ('direct', 'Direct'),
        ('group', 'Group'),
    )
    
    name = models.CharField(max_length=255, null=True, blank=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='direct')
    members = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chats_chatroom'  # Chỉ định tên bảng nếu có vấn đề tương tự
    
    @classmethod
    def get_or_create_direct_room(cls, user1, user2):
        """Tìm hoặc tạo phòng chat 1-1 giữa hai người dùng"""
        try:
            # Tìm phòng chat 1-1 giữa hai người
            rooms = ChatRoom.objects.filter(room_type='direct', members=user1).filter(members=user2)
            
            if rooms.exists():
                return rooms.first()
            else:
                # Tạo phòng mới nếu chưa tồn tại
                room = ChatRoom.objects.create(room_type='direct')
                room.members.add(user1, user2)
                return room
        except Exception as e:
            print(f"Error in get_or_create_direct_room: {str(e)}")
            raise

    def __str__(self):
        if self.room_type == 'direct':
            members = self.members.all()
            if members.count() == 2:
                return f"Chat between {members[0].username} and {members[1].username}"
        return self.name or f"Group {self.id}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Xóa bỏ class Meta và db_table để sử dụng quy ước đặt tên mặc định của Django
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"
