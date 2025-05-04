import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chats.models import Message, ChatRoom
from users.models import User
import logging
import traceback

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    # Sử dụng biến class thay vì instance để lưu trữ kết nối
    user_sockets = {}  

    async def connect(self):
        self.user_id = self.scope["path"].split("/")[-2]
        self.group_name = f"user_{self.user_id}"

        # Lưu kết nối của user
        ChatConsumer.user_sockets[self.user_id] = self.channel_name
        
        # Thêm người dùng vào group chat của họ
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        logger.info(f"User {self.user_id} connected. Total connections: {len(ChatConsumer.user_sockets)}")

        # Thông báo danh sách người dùng online
        await self.send(text_data=json.dumps({
            "type": "users_online",
            "users": list(ChatConsumer.user_sockets.keys())
        }))

    async def disconnect(self, close_code):
        try:
            # Xóa kết nối và thông báo cho các user khác
            if hasattr(self, 'user_id') and self.user_id in ChatConsumer.user_sockets:
                del ChatConsumer.user_sockets[self.user_id]
                
                # Rời khỏi group
                await self.channel_layer.group_discard(self.group_name, self.channel_name)
                
                # Thông báo user disconnect
                for user_id in ChatConsumer.user_sockets:
                    await self.channel_layer.group_send(
                        f"user_{user_id}",
                        {
                            "type": "user_disconnected",
                            "userId": self.user_id
                        }
                    )
                
                logger.info(f"User {self.user_id} disconnected. Remaining: {len(ChatConsumer.user_sockets)}")
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")

    async def receive(self, text_data):
        try:
            if not text_data:
                logger.warning("Received empty message.")
                return

            data = json.loads(text_data)
            event_type = data.get("type")
            logger.info(f"Received event: {event_type}, from user: {self.user_id}")

            if event_type == "send_message":
                sender_id = data["senderId"]
                content = data["content"]
                
                # Xử lý cả direct message và group message
                if "roomId" in data:
                    await self._handle_group_message(sender_id, data["roomId"], content)
                else:
                    await self._handle_direct_message(sender_id, data["receiverId"], content)
                    
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            logger.error(traceback.format_exc())
            # Gửi lỗi về client thay vì đóng kết nối
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"Server error: {str(e)}"
            }))

    async def _handle_direct_message(self, sender_id, receiver_id, content):
        try:
            # Lưu tin nhắn và lấy ID
            message_id, chat_room_id = await self.save_message(sender_id, receiver_id, content)
            
            # Format tin nhắn để gửi
            message = {
                "id": str(message_id),
                "senderId": sender_id,
                "receiverId": receiver_id,
                "roomId": str(chat_room_id),
                "content": content,
                "createdAt": str(await self.get_message_timestamp(message_id))
            }
            
            # Gửi đến người nhận
            receiver_group = f"user_{receiver_id}"
            await self.channel_layer.group_send(
                receiver_group,
                {
                    "type": "receive_message",
                    "message": message
                }
            )
            
            # Gửi lại cho người gửi
            sender_group = f"user_{sender_id}"
            if sender_group != receiver_group:  # Không gửi hai lần nếu là tin nhắn với chính mình
                await self.channel_layer.group_send(
                    sender_group,
                    {
                        "type": "receive_message",
                        "message": message
                    }
                )
            
            logger.info(f"Message sent from {sender_id} to {receiver_id}")
        except Exception as e:
            logger.error(f"Error sending direct message: {str(e)}")
            raise

    async def _handle_group_message(self, sender_id, room_id, content):
        try:
            message_id, chat_room_id = await self.save_message(
                sender_id=sender_id,
                receiver_id=None,
                content=content,
                room_id=room_id
            )
            
            # Lấy tất cả member IDs trong room
            member_ids = await self.get_room_member_ids(room_id)
            
            # Format message response
            message = {
                "id": str(message_id),
                "senderId": sender_id,
                "roomId": str(chat_room_id),
                "content": content,
                "createdAt": str(await self.get_message_timestamp(message_id))
            }
            
            # Gửi đến tất cả thành viên trong room
            for member_id in member_ids:
                member_group = f"user_{member_id}"
                await self.channel_layer.group_send(
                    member_group,
                    {
                        "type": "receive_message",
                        "message": message
                    }
                )
            
            logger.info(f"Group message sent from {sender_id} to room {room_id}")
        except Exception as e:
            logger.error(f"Error sending group message: {str(e)}")
            raise

    async def receive_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "receive_message",
            "message": event["message"]
        }))
    
    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content, room_id=None):
        try:
            logger.info(f"Saving message from {sender_id} to {receiver_id}, content: {content[:20]}...")
            
            # Kiểm tra xem sender có tồn tại không
            try:
                sender = User.objects.get(id=sender_id)
            except User.DoesNotExist:
                logger.error(f"Sender with ID {sender_id} not found")
                raise ValueError(f"Sender with ID {sender_id} not found")
            
            # Xử lý trường hợp room_id được cung cấp
            if room_id:
                try:
                    chat_room = ChatRoom.objects.get(id=room_id)
                    receiver = None
                    logger.info(f"Found room {room_id} for group message")
                except ChatRoom.DoesNotExist:
                    logger.error(f"Chat room with ID {room_id} not found")
                    raise ValueError(f"Chat room with ID {room_id} not found")
            else:
                # Xử lý tin nhắn 1-1
                try:
                    receiver = User.objects.get(id=receiver_id)
                except User.DoesNotExist:
                    logger.error(f"Receiver with ID {receiver_id} not found")
                    raise ValueError(f"Receiver with ID {receiver_id} not found")
                
                # Tìm hoặc tạo phòng chat 1-1
                try:
                    chat_room = ChatRoom.get_or_create_direct_room(sender, receiver)
                    logger.info(f"Using direct chat room {chat_room.id} for message")
                except Exception as e:
                    logger.error(f"Error creating direct chat room: {str(e)}")
                    raise
            
            # Tạo tin nhắn
            try:
                message = Message.objects.create(
                    sender=sender,
                    receiver=receiver,
                    chat_room=chat_room,
                    content=content
                )
                logger.info(f"Message saved with ID: {message.id}")
                return str(message.id), str(chat_room.id)  # Chuyển UUID thành string
            except Exception as e:
                logger.error(f"Error creating message: {str(e)}")
                raise
                
        except Exception as e:
            logger.error(f"Error in save_message: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    @database_sync_to_async
    def get_message_timestamp(self, message_id):
        return Message.objects.get(id=message_id).created_at
    
    @database_sync_to_async
    def get_room_member_ids(self, room_id):
        room = ChatRoom.objects.get(id=room_id)
        return list(room.members.values_list('id', flat=True))
