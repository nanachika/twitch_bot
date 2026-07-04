import os
import asyncio
import logging
from dotenv import load_dotenv

import twitchio
from twitchio import eventsub
from twitchio.ext import commands

import random as rn

import json as js

load_dotenv()

# Загружаем твои настройки
token = os.getenv("TWITCH_TOKEN")
client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")
bot_id = os.getenv("TWITCH_BOT_ID")
id_channel = os.getenv("ID_CHANNEL")


# 1. КЛАСС БОТА (Отвечает только за подключение и события)
class TwitchBot(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            token=token,# type: ignore
            prefix="!",
            client_id=client_id,
            client_secret=client_secret,
            bot_id=bot_id
        )

    async def setup_hook(self) -> None:
        # Подключаем вебсокет для чтения чата
        payload = eventsub.ChatMessageSubscription(
            broadcaster_user_id=id_channel, 
            user_id=self.bot_id
        )
        await self.subscribe_websocket(payload=payload, token_for=self.bot_id)

        await self.add_component(ChatCommands(self))
        print("Система команд успешно загружена!")

    async def event_ready(self) -> None:
        print('Бот подключился к каналу и слушает чат!')
        my_chat = self.create_partialuser(id_channel)# type: ignore
        await my_chat.send_message(message='Бот на месте DinoDance', sender=self.user)# type: ignore
    
    async def event_message(self, payload) -> None:
        if payload.chatter.id == self.bot_id:
            return

        print(f"[{payload.broadcaster.name}] {payload.chatter.name}: {payload.text}")
        
        # Передаем сообщение дальше, чтобы компоненты его услышали
        await super().event_message(payload)


# 2. КОМПОНЕНТ С КОМАНДАМИ (Тут живут все!команды)
class ChatCommands(commands.Component):

    def __init__(self, bot: TwitchBot) -> None:
        self.bot = bot

    @commands.command(name='привет')
    async def hello_command(self, ctx: commands.Context) -> None:
        print("Ура! Команда !привет сработала через официальный Компонент!")
        # Отправляем сообщение, используя объект бота из конструктора (self.bot.user)
        await ctx.channel.send_message(message='Привет! DinoDance', sender=self.bot.user) # type: ignore
    
    @commands.command(name='обнять')
    async def hug_command(self, ctx: commands.Context) -> None:
        # 1. Проверяем, загрузился ли аккаунт бота
        if not self.bot.user:
            return
        
        chatter_list = []
        
        # 2. Получаем специальный объект от Твича через ID нашего бота
        users_box = await ctx.channel.fetch_chatters(moderator=self.bot.user.id)
        
        # 3. Заходим в список пользователей (.users) внутри этого объекта
        async for chatter in users_box.users:
            # Отсеиваем самого бота, чтобы он сам себя не обнимал
           if chatter.id != self.bot.user.id and chatter.id != ctx.chatter.id:
                chatter_list.append(chatter)
        
        # 4. Если в чате никого нет, кроме бота
        if not chatter_list:
            await ctx.channel.send_message(
                message=f'{ctx.chatter.name} обнимает сам себя... ::>_<::', 
                sender=self.bot.user
            )
            return
        
        # 5. Выбираем случайного счастливчика и отправляем красивое имя в чат
        random_user = rn.choice(chatter_list)
        await ctx.channel.send_message(
            message=f'{ctx.chatter.name} обнял {random_user.name} :3 DinoDance', 
            sender=self.bot.user
        )
    @commands.command(name='смерть')
    async def count_death(self, ctx: commands.Context, amount: str='1') -> None:
        if not self.bot.user:
            return
        
        if amount == 'список':
            with open('death.json', 'r') as f:
                games = js.load(f)
                
            # 1. Создаем пустой список для записей
            games_list = []
            
            # 2. Наполняем его чистыми строками (без всяких запятых на конце)
            for game_name, death_count in games.items():
                games_list.append(f'{game_name} - {death_count}') 

            # 3. Склеиваем всё через запятую с пробелом и добавляем заголовок
            message_text = '📋 Список смертей: ' + ', '.join(games_list)

            await ctx.channel.send_message(
                message=message_text, 
                sender=self.bot.user
            )
            return

        if (not ctx.chatter.is_mod) and (not ctx.chatter.is_broadcaster):
            return
        
        points = 1
        channel_info = await self.bot.fetch_channel(broadcaster_id=ctx.channel.id)
        current_game = channel_info.game_name
        
        if amount.isdigit():
            points = int(amount)

        with open('death.json', 'r') as f:
            data = js.load(f)
            data[current_game] = data.get(current_game,0)+points
            
        with open('death.json', 'w') as f:
            js.dump(data,f)
        
        await ctx.channel.send_message(
            message=f'В игре: {current_game} количество смертей: {data[current_game]}, ', 
            sender=self.bot.user
        )
    
    @commands.command(name='команды')
    async def commands(self, ctx: commands.Context) -> None:
        if not self.bot.user:
            return
        all_commands = ', !'.join(self.bot.commands.keys())
        await ctx.channel.send_message(
            message=f'Доступные команды: !{all_commands}', 
            sender=self.bot.user)

# 3. ТОЧКА ЗАПУСКА (Красивый асинхронный запуск, как в примере)
def main() -> None:
    # Включаем логирование от самой библиотеки (будет видно все внутренние процессы)
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with TwitchBot() as bot:
            await bot.start()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        print("Бот успешно выключен.")

if __name__ == "__main__":
    main()