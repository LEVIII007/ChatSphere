import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from gpt.query import perform_query_search
from gpt.chat import Response
# from .models import ChatMessage


# form langchian_core.messages import HumanMessage, AIMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = "user"
        self.room_group_name = f'chat_{self.username}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("connected")  # Debugging

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': 'user'
        }))

        bot_response = await get_bot_response(message)

        await self.send(text_data=json.dumps({
            'message': bot_response,
            'sender': 'ChatSphere'
        }))

async def get_bot_response(user_message):
    return Response(user_message)


