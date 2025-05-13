from django.db import models
import uuid
from users.models import User

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    CONVERSATION_TYPES = (
        ('direct', 'Direct'),
        ('group', 'Group'),
    )
    
    name = models.CharField(max_length=255, null=True, blank=True)
    conversation_type = models.CharField(max_length=10, choices=CONVERSATION_TYPES, default='direct')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
    
    @classmethod
    def get_or_create_direct_conversation(cls, user1, user2):
        try:
            conversations = Conversation.objects.filter(
                conversation_type='direct',
                conversationmember_set__user=user1
            ).filter(
                conversationmember_set__user=user2
            )
            if conversations.exists():
                return conversations.first()
            else:
                conversation = Conversation.objects.create(conversation_type='direct')
                ConversationMember.objects.create(conversation=conversation, user=user1)
                ConversationMember.objects.create(conversation=conversation, user=user2)
                return conversation
        except Exception as e:
            print(f"Error in get_or_create_direct_conversation: {str(e)}")
            raise

    def get_display_name(self, current_user):
        if self.conversation_type == 'direct':
            other_member = self.conversationmember_set.exclude(user=current_user).first()
            if other_member and hasattr(other_member, "user"):
                return other_member.user.fullName or other_member.user.username
            return "Private Conversation"
        else:
            return self.name or f"Group Conversation {self.id}"

    def __str__(self):
        if self.conversation_type == 'direct':
            members = [member.user.username for member in self.conversationmember_set.all()[:2]]
            if len(members) == 2:
                return f"Chat between {members[0]} and {members[1]}"
        return self.name or f"Group {self.id}"


class ConversationMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='conversationmember_set')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'conversation_members'
        unique_together = ('conversation', 'user')
    
    def __str__(self):
        return f"{self.user.username} in {self.conversation}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"