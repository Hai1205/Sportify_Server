import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chats.models import Message, Conversation, ConversationMember
from users.models import User
from django.utils import timezone
import logging
import traceback

logger = logging.getLogger(__name__)

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

def convert_uuid_to_str(data):
    if data is None:
        return None
    if isinstance(data, uuid.UUID):
        return str(data)
    elif isinstance(data, dict):
        return {convert_uuid_to_str(k): convert_uuid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_uuid_to_str(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(convert_uuid_to_str(item) for item in data)
    elif hasattr(data, '__dict__') and not isinstance(data, type):
        try:
            dict_representation = data.__dict__
            return {convert_uuid_to_str(k): convert_uuid_to_str(v) for k, v in dict_representation.items()}
        except Exception as e:
            logger.error(f"CONV_UUID: Error converting __dict__ of {type(data)}: {e}. Falling back to str(). Data: {str(data)[:200]}")
            return str(data) 
    return data

class ChatConsumer(AsyncWebsocketConsumer):
    user_sockets = {}  

    async def connect(self):
        self.user_id = self.scope["path"].split("/")[-2]
        self.group_name = f"user_{self.user_id}"
        ChatConsumer.user_sockets[self.user_id] = self.channel_name
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        logger.info(f"User {self.user_id} connected. Total connections: {len(ChatConsumer.user_sockets)}")

        await self.send(text_data=json.dumps({
            "type": "users_online",
            "users": list(ChatConsumer.user_sockets.keys())
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        if hasattr(self, 'user_id') and self.user_id in ChatConsumer.user_sockets:
            del ChatConsumer.user_sockets[self.user_id]
            logger.info(f"User {self.user_id} disconnected. Total connections: {len(ChatConsumer.user_sockets)}")

    async def receive(self, text_data):
        try:
            if not text_data:
                logger.warning("Received empty message")
                return

            data = json.loads(text_data)
            event_type = data.get("type")
            logger.info(f"Received event: {event_type} from user: {self.user_id}")

            if event_type == "send_message":
                sender_id = data["senderId"]
                content = data["content"]
                conversation_id = data.get("conversationId")
                sender_id_str = str(sender_id)
                conversation_id_str = str(conversation_id)
                
                if not conversation_id_str:
                    await self.send(text_data=json.dumps({"type": "error", "message": "conversationId is required"}))
                    return
                
                message_id = await self.save_message(sender_id_str, conversation_id_str, content)
            
                raw_message_data_from_db = await self.get_message_data(message_id) 
                final_message_data_for_group = convert_uuid_to_str(raw_message_data_from_db)
                
                member_ids = [str(m_id) for m_id in await self.get_conversation_member_ids(conversation_id_str)]
                
                for member_id_str in member_ids:
                    member_group = f"user_{member_id_str}"
                    
                    payload_for_group = {
                        "type": "receive_message", 
                        "message": final_message_data_for_group,
                    }
                    
                    fully_converted_payload_for_group = convert_uuid_to_str(payload_for_group)
                    
                    await self.channel_layer.group_send(
                        member_group,
                        fully_converted_payload_for_group
                    )
            
            elif event_type == "mark_as_read":
                conversation_id = str(data.get("conversationId"))
                if not conversation_id:
                    await self.send(text_data=json.dumps({"type": "error", "message": "conversationId is required"}))
                    return
                
                await self.mark_conversation_as_read(self.user_id, conversation_id)
                await self.send(text_data=json.dumps({"type": "messages_read", "conversationId": conversation_id}))
            
            elif event_type == "join_room":
                room_id = str(data.get("roomId")) 
                room_group = f"room_{room_id}"
                await self.channel_layer.group_add(room_group, self.channel_name)
                
        except Exception as e:
            logger.error(f"Error processing received WebSocket message: {str(e)}")
            logger.error(traceback.format_exc())
            await self.send(text_data=json.dumps({"type": "error", "message": f"An error occurred: {str(e)}"}, cls=UUIDEncoder, default=str))

    async def receive_message(self, event): 
        try:
            message_payload = event.get("message", {})

            final_cleaned_message_for_client = convert_uuid_to_str(message_payload)

            output_data_to_client = {
                "type": "new_message",
                "message": final_cleaned_message_for_client
            }

            json_string = json.dumps(output_data_to_client, cls=UUIDEncoder, default=str)
            await self.send(text_data=json_string)
            
        except TypeError as te:
            logger.error(f"FINAL DUMP TypeError in receive_message: {str(te)}. Event data: {str(event)[:500]}")
            logger.error(traceback.format_exc())
            stringified_message_content = {str(k): str(v) for k, v in event.get("message", {}).items()}
            await self.send(text_data=json.dumps({"type": "new_message", "message": stringified_message_content}, default=str))
                
        except Exception as e:
            logger.error(f"Error in receive_message handler: {str(e)}")
            logger.error(traceback.format_exc())
            await self.send(text_data=json.dumps({"type": "error", "message": "Could not process message for client."}, cls=UUIDEncoder, default=str))

    @database_sync_to_async
    def save_message(self, sender_id, conversation_id, content):
        try:
            logger.info(f"Saving message from {sender_id} in conversation {conversation_id}")
            
            sender = User.objects.get(id=uuid.UUID(sender_id)) 
            conversation = Conversation.objects.get(id=uuid.UUID(conversation_id))
            
            if not ConversationMember.objects.filter(conversation=conversation, user=sender).exists():
                raise ValueError("User is not a member of this conversation")
            
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                content=content
            )
            
            conversation.updated_at = timezone.now()
            conversation.save()
            
            logger.info(f"Message saved with ID: {message.id}")
            return str(message.id)
            
        except Exception as e:
            logger.error(f"Error in save_message: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    @database_sync_to_async
    def get_message_data(self, message_id):
        from chats.serializers import MessageSerializer 

        message = Message.objects.get(id=uuid.UUID(message_id))
        serialized_data = MessageSerializer(message).data

        return convert_uuid_to_str(serialized_data) 
    
    @database_sync_to_async
    def get_conversation_member_ids(self, conversation_id_str):
        members = ConversationMember.objects.filter(conversation_id=uuid.UUID(conversation_id_str)) # Query with UUID
        return [str(member.user.id) for member in members] 
    
    @database_sync_to_async
    def mark_conversation_as_read(self, user_id_str, conversation_id_str):
        try:
            member = ConversationMember.objects.get(
                conversation_id=uuid.UUID(conversation_id_str), 
                user_id=uuid.UUID(user_id_str) 
            )
            member.last_read_at = timezone.now()
            member.save()
            return True
        except ConversationMember.DoesNotExist:
            logger.warning(f"User {user_id_str} is not a member of conversation {conversation_id_str}")
            return False
