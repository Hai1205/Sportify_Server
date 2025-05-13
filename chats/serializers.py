from rest_framework import serializers
from .models import Message, Conversation, ConversationMember
from users.serializers import UserSerializer

#lỗi n+1 querry

class MessageSerializer(serializers.ModelSerializer):
    sender_data = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_data', 'content', 'created_at', 'updated_at', 'is_read']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ConversationMemberSerializer(serializers.ModelSerializer):
    user_data = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = ConversationMember
        fields = ['id', 'conversation', 'user', 'user_data', 'role', 'joined_at', 'last_read_at']
        read_only_fields = ['id', 'joined_at']

class ConversationSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'name', 'conversation_type', 'members', 'created_at', 
                 'updated_at', 'last_message', 'unread_count', 'display_name']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_members(self, obj):
        members = ConversationMember.objects.filter(conversation=obj)
        return ConversationMemberSerializer(members, many=True).data
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
    
    def get_unread_count(self, obj):
        user = self.context.get('user')
        if not user:
            return 0
        
        member = ConversationMember.objects.filter(conversation=obj, user=user).first()
        if not member or not member.last_read_at:
            return obj.messages.exclude(sender=user).count()
        
        return obj.messages.exclude(sender=user).filter(created_at__gt=member.last_read_at).count()
    
    def get_display_name(self, obj):
        user = self.context.get('user')
        if not user:
            return obj.name or str(obj.id)
        
        return obj.get_display_name(user)