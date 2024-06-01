import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room

class WSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'room_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Retrieve the current state of the room from the database
        room_text = await self.get_room_text(self.room_group_name)
        await self.send(text_data=json.dumps({
            'message': room_text
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)['message']

        # Save the message to the database
        await self.save_room_text(self.room_group_name, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @sync_to_async
    def get_room_text(self, room_name):
        room, created = Room.objects.get_or_create(name=room_name)
        return room.text

    @sync_to_async
    def save_room_text(self, room_name, text):
        room, created = Room.objects.get_or_create(name=room_name)
        room.text = text
        room.save()
