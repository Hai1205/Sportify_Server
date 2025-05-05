"""
ASGI config for api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django

# Đặt biến môi trường
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sportify_server.settings')

# Khởi tạo Django hoàn chỉnh TRƯỚC KHI import các model
django.setup()

# Sau khi Django được khởi tạo hoàn tất, giờ có thể import các module khác
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

