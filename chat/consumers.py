import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, ChatGroup
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add('presence', self.channel_name)
        await self.accept()

        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_send('presence', {
                'type': 'presence.update',
                'username': user.username,
                'status': 'online',
            })
            await self.channel_layer.group_add(f'presence_user_{user.username}', self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard('presence', self.channel_name)
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_send('presence', {
                'type': 'presence.update',
                'username': user.username,
                'status': 'offline',
            })
            try:
                await self.channel_layer.group_discard(f'presence_user_{user.username}', self.channel_name)
            except Exception:
                pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        author = self.scope['user']
        content = data.get('message','')
        if author.is_authenticated:
            await database_sync_to_async(self.save_message)(author, content)
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'message': content,
            'sender': author.username if author.is_authenticated else 'Anonymous',
            'timestamp': timezone.now().isoformat(),
        })

    def save_message(self, user, content):
        Message.objects.create(sender=user, content=content, room_name=self.room_name,
                               is_group=self.room_name.startswith('group_'))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event.get('message'),
            'sender': event.get('sender'),
            'timestamp': event.get('timestamp'),
        }))

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'username': event.get('username'),
            'status': event.get('status'),
        }))
