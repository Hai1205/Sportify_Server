import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    user_sockets = {}  # { userId: socket_id }

    async def connect(self):
        self.user_id = self.scope["path"].split("/")[-2]
        self.group_name = f"user_{self.user_id}"

        self.user_sockets[self.user_id] = self.channel_name

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        print(f"User {self.user_id} connected.")

        await self.send(text_data=json.dumps({
            "type": "users_online",
            "users": list(self.user_sockets.keys())
        }))

    async def disconnect(self, close_code):
        disconnected_user_id = None
        for user_id, socket_id in self.user_sockets.items():
            if socket_id == self.channel_name:
                disconnected_user_id = user_id
                del self.user_sockets[user_id]
                break
        
        if disconnected_user_id:
            await self.channel_layer.group_discard(f"user_{disconnected_user_id}", self.channel_name)
            await self.channel_layer.group_send(
                "chat_group",
                {"type": "user_disconnected", "user_id": disconnected_user_id},
            )

    async def receive(self, text_data):
        if not text_data:
            print("Received empty message.")
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return

        event_type = data.get("type")
        print(f"Received event: {event_type}, data: {data}")

        if event_type == "user_connected":
            user_id = data["userId"]
            self.user_sockets[user_id] = self.channel_name
            await self.channel_layer.group_add(f"user_{user_id}", self.channel_name)  # Thêm user vào nhóm riêng
            await self.send(text_data=json.dumps({"type": "users_online", "users": list(self.user_sockets.keys())}))

        elif event_type == "send_message":
            sender_id = data["senderId"]
            receiver_id = data["receiverId"]
            content = data["content"]

            # Gửi đến group của receiver
            receiver_group = f"user_{receiver_id}"
            await self.channel_layer.group_send(
                receiver_group,
                {
                    "type": "receive_message",
                    "senderId": sender_id,
                    "content": content,
                }
            )
            print(f"Message sent from {sender_id} to {receiver_id}")

    async def receive_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "receive_message",
            "senderId": event["senderId"],
            "content": event["content"],
        }))
