import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Club, FriendlyGame, Player


class FriendlyGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.club_id = self.scope['url_route']['kwargs']['club_id']
        self.room_group_name = f'friendly_game_{self.club_id}'

        # Присоединиться к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Покинуть группу
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Получить сообщение от WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'game_update':
            # Отправить обновление всем в группе
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_update_message',
                    'game_data': data.get('game_data')
                }
            )
        elif message_type == 'game_end':
            # Отправить уведомление об окончании игры
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_end_message',
                    'game_data': data.get('game_data')
                }
            )

    # Обработчик для отправки обновлений игры
    async def game_update_message(self, event):
        game_data = event['game_data']

        # Отправить сообщение клиенту
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'game_data': game_data
        }))

    # Обработчик для завершения игры
    async def game_end_message(self, event):
        game_data = event['game_data']

        # Отправить сообщение клиенту
        await self.send(text_data=json.dumps({
            'type': 'game_end',
            'game_data': game_data
        }))
