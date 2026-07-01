import os
import asyncio
import logging
from dotenv import load_dotenv

import twitchio
from twitchio import eventsub
from twitchio.ext import commands

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

        # МАГИЯ ИЗ ДОКУМЕНТАЦИИ: Насильно регистрируем компонент с командами
        await self.add_component(ChatCommands(self))
        print("Система команд успешно загружена!")

    async def event_ready(self) -> None:
        print('Бот подключился к каналу и слушает чат!')
        my_chat = self.create_partialuser(id_channel)# type: ignore
        await my_chat.send_message(message='Бот на месте DinoDance', sender=self.user)# type: ignore
    
    async def event_message(self, payload) -> None:
        if payload.chatter.id == self.bot_id:
            return

        # Твой красивый двойной вывод в консоль
        print(f"[{payload.broadcaster.name}] {payload.chatter.name}: {payload.text}")
        
        # Передаем сообщение дальше, чтобы компоненты его услышали
        await super().event_message(payload)


# 2. КОМПОНЕНТ С КОМАНДАМИ (Тут живут все твои !команды)
class ChatCommands(commands.Component):

    def __init__(self, bot: TwitchBot) -> None:
        self.bot = bot

    @commands.command(name='привет')
    async def hello_command(self, ctx: commands.Context) -> None:
        print("Ура! Команда !привет сработала через официальный Компонент!")
        # Отправляем сообщение, используя объект бота из конструктора (self.bot.user)
        await ctx.channel.send_message(message='Привет! DinoDance', sender=self.bot.user) # type: ignore


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