from django.urls import re_path
from your_app import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/<str:user_name>/', consumers.ChatConsumer.as_asgi()),
]
