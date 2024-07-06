import json
from channels.generic.websocket import AsyncWebsocketConsumer
from gpt.query import perform_query_search
# from .models import ChatMessage


form langchian_core.messages import HumanMessage, AIMessage

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

        # Send past messages
        # past_messages = ChatMessage.objects.filter(user=self.username).order_by('timestamp')
        # for message in past_messages:
        #     await self.send(text_data=json.dumps({
        #         'message': message.message,
        #         'sender': message.sender
        #     }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']


        chat_history = [
            HumanMessage(text="Hello, how are you? my name is leon"),
            AIMessage(text="I'm fine, thank you!"),
            HumanMessage(text="What's the weather like today?"),
            AIMessage(text="It's sunny today!"),
        ]


        response = 



















        # Save user message
        # ChatMessage.objects.create(user=self.username, message=message, sender='user')

        # Send user message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': 'user'
        }))

        # Get bot response
        bot_response = get_bot_response(message)
        # Save bot response
        # ChatMessage.objects.create(user=self.username, message=bot_response, sender='bot')

        # Send bot response to WebSocket
        await self.send(text_data=json.dumps({
            'message': bot_response,
            'sender': 'bot'
        }))

def get_bot_response(user_message):
    # Implement your AI bot response logic here
    return perform_query_search(user_message)













# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# # from ChatApp.models import *

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
#         await self.channel_layer.group_add(self.room_name, self.channel_name)
#         await self.accept()
        
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_name, self.channel_name)

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json

#         event = {
#             'type': 'send_message',
#             'message': message,
#         }

#         await self.channel_layer.group_send(self.room_name, event)

#     async def send_message(self, event):

#         data = event['message']
#         await self.create_message(data=data)

#         response_data = {
#             'sender': data['sender'],
#             'message': data['message']
#         }
#         await self.send(text_data=json.dumps({'message': response_data}))

#     # @database_sync_to_async
#     # def create_message(self, data):

#     #     get_room_by_name = Room.objects.get(room_name=data['room_name'])
        
#     #     if not Message.objects.filter(message=data['message']).exists():
#     #         new_message = Message(room=get_room_by_name, sender=data['sender'], message=data['message'])
#     #         new_message.save()

