from asgiref.sync import async_to_sync as AtoS
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.job_group_name = 'job_%s' % self.job_id
        await self.channel_layer.group_add(
            self.job_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.job_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        status = text_data_json['status']
        action = text_data_json['action']
        task_id = text_data_json['task_id']

        await self.channel_layer.group_send(self.job_group_name,{
            'type':'task_message',
            'status': status,
            'action': action,
            'task_id': task_id
        })
    async def task_message(self, event):
        status = event['status']
        action = event['action']
        task_id = event['task_id']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'status': status,
            'action': action,
            'task_id': task_id
        }))
