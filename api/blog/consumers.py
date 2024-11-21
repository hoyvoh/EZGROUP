import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.group_name = f"post_{self.post_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'new_comment':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send_comment",
                    "comment_data": data['comment_data'],
                }
            )
        elif action == 'new_notification':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send_notification",
                    "notification_data": data['notification_data'],
                }
            )

    async def send_comment(self, event):
        await self.send(text_data=json.dumps({
            "type": "comment",
            "data": event["comment_data"]
        }))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "notification",
            "data": event["notification_data"]
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f"user_{self.scope['user'].id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
