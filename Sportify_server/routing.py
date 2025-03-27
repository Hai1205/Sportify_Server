from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<user_id>[0-9a-fA-F-]{36})/$", ChatConsumer.as_asgi()),
]

# run command: daphne -p 8001 Sportify_Server.asgi:application