import websockets
import websockets.exceptions
import asyncio

from .config import *
from .events import *


class Client:
    def __init__(self, client_token=None):
        self.ws = config['ws']
        self.http = config['http']
        self.url = config['url']
        self.token = client_token
        self.header = {'Authorization': f'Token {client_token}'}

        self.websockets = {}

        self.user = None
        self.membership = None
        self.guilds = []

    def _get_user(self):
        self.user = requests.get(f'{self.http}://{self.url}/api/me/', headers=self.header).json()

    def _get_membership(self):
        self.membership = requests.get(f'{self.http}://{self.url}/api/me/membership/', headers=self.header).json().get('membership', [])

    def _get_guilds(self):
        for member in self.membership:
            self.guilds.append(member.get('guild'))

    # Получение информации о боте
    def setup(self):
        self._get_membership()
        self._get_guilds()
        self._get_user()

    # необходимо вызвать метод для запуска бота
    def run(self):
        if self.token:
            self.setup()
            self._start()

    # Запуск AsyncIO
    def _start(self):
        loop = asyncio.get_event_loop()

        loop.create_task(self.new_guild_connector(loop))

        for member in self.membership:
            loop.create_task(self._start_loop(member, loop=loop))

        self.on_ready()
        loop.run_forever()

    # Вызывается при готовности бота к работе
    def on_ready(self):
        print('-------')
        print('Logged on as {}!'.format(self.user.get('username')))
        print('-------')
        print('Guilds:')
        for guild in self.guilds:
            print(guild.get('name'))
        print('-------')

    # Подключение к новым гильдиям во время работы
    async def new_guild_connector(self, loop):
        async with websockets.connect(uri=f'{self.ws}://{self.url}/ws/bot/', extra_headers=self.header, ping_interval=20) as websocket:
            self.websockets['bot'] = websocket

            while True:
                event = await websocket.recv()
                event = json.loads(event)
                if event.get('action') == 'joined':
                    member_id = event.get('member_id')
                    response = requests.get(f'{self.http}://{self.url}/api/member/{member_id}/', headers=self.header).json()
                    self.membership.append(response)
                    self.guilds.append(response.get('guild'))
                    loop.create_task(self._start_extra_loop(event.get('guild_id'), loop=loop))

    # Цикл к новым гильдиям во время работы
    async def _start_extra_loop(self, guild_id, loop):
        async with websockets.connect(uri=f'{self.ws}://{self.url}/ws/chat/{guild_id}/', extra_headers=self.header, ping_interval=20) as websocket:
            print('Connect to new guild!')
            self.websockets[f'{guild_id}'] = websocket

            while True:
                event = await websocket.recv()
                event = json.loads(event)
                if event.get('action') == 'send':
                    loop.create_task(self.on_message(Message(event, client=self)))
                elif event.get('action') == 'joined':
                    loop.create_task(self.on_join(Join(event, client=self)))

    # Цикл к уже существующим гильдиям на момент запуска
    async def _start_loop(self, member, loop):
        guild_id = member['guild']['id']
        async with websockets.connect(uri=f'{self.ws}://{self.url}/ws/chat/{guild_id}/', extra_headers=self.header, ping_interval=20) as websocket:
            self.websockets[f'{guild_id}'] = websocket

            while True:
                event = await websocket.recv()
                event = json.loads(event)
                if event.get('action') == 'send':
                    loop.create_task(self.on_message(Message(event, client=self)))
                elif event.get('action') == 'joined':
                    loop.create_task(self.on_join(Join(event, client=self)))

    # Вызывается при новом сообщении
    async def on_message(self, message: Message):
        pass

    # Вызывается при новом участнике гильдии
    async def on_join(self, event: Join):
        pass
