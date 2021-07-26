import datetime
import json

import requests

from .config import *


class Message:
    def __init__(self, event, client=None):
        self.client = client

        self.id = event['message']['id']
        self.guild: Guild = Guild(event['guild']['id'], self.client)
        self.author: Member = Member(event['author']['id'], self.client)
        self.content: str = event['message']['text']
        self.created_at: datetime.datetime = event['message']['created_at']
        self.modified_at: datetime.datetime = event['message']['modified_at']

        self.args: str = self._get_args()

    async def delete(self):
        ws = self.client.websockets.get(f'{self.guild.id}')
        await ws.send(json.dumps({
            'action': 'delete',
            'message_id': f'{self.id}'
        }))

    def startwith(self, header: str):
        message = self.content.split(maxsplit=1)
        try:
            if message[0] == header:
                return True
        except:
            pass
        return False

    def _get_args(self):
        message = self.content.split(maxsplit=1)
        try:
            return message[1]
        except:
            return ''


class Join:
    def __init__(self, event, client=None):
        self.client = client

        self.member: Member = Member(event['member']['id'], client=client)


class Guild:
    def __init__(self, guild_id, client=None):
        self.client = client

        guild = requests.get(f'{self.client.http}://{self.client.url}/api/guild/{guild_id}/', headers=client.header).json()
        self.id = guild.get('id')
        self.name = guild.get('name')
        self.created_at = guild.get('created_at')
        self.creator = User(guild.get('creator'), client=self.client)

    async def send(self, message: str):
        ws = self.client.websockets.get(f'{self.id}')
        await ws.send(json.dumps({
            'action': 'send',
            'message': f'{message}'
        }))

    async def clear(self, limit: int):
        ws = self.client.websockets.get(f'{self.id}')
        await ws.send(json.dumps({
            'action': 'clear',
            'limit': limit
        }))


class User:
    def __init__(self, user_id, client=None):
        self.client = client


class Member:
    def __init__(self, member_id, client=None):
        self.client = client

        member = requests.get(f'{self.client.http}://{self.client.url}/api/member/{member_id}/', headers=client.header).json()
        self.id = member['id']
        self.user = member['user']['id']
        self.username = member['user']['username']
        self.bot = member['user']['bot']
        self.admin = member['admin']
        self.active = member['active']
        self.banned = member['banned']
        self.guild = Guild(member['guild']['id'], client=self.client)

        if member['user']['first_name'] and member['user']['last_name']:
            self.username = '{} {}'.format(member['user']['first_name'], member['user']['last_name'])
