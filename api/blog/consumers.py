import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.room_group_name = f'comments_{self.post_id}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        comment = data['comment']
        user = self.scope['user'].username  # Ensure user authentication is handled

        # Send comment to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'comment_message',
                'comment': comment,
                'user': user,
            }
        )

    async def comment_message(self, event):
        comment = event['comment']
        user = event['user']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'comment': comment,
            'user': user,
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'notifications'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Custom logic for receiving data (e.g., a user triggers a notification)
        pass

    async def notification_message(self, event):
        message = event['message']

        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
        }))
