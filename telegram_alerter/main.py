import asyncio
import aio_pika
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from database import engine, Base
from config import API_TOKEN, RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_PORT, RABBITMQ_LOGIN
from utils import add_user, get_users

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user = message.from_user
    chat = message.chat
    await add_user(user.id, chat.id)
    await message.answer(f"Вы успешно подписались на рассылку о новых лотах")


async def send_message_to_all_users(message: str):
    users_chats = await get_users()
    for chat in users_chats:
        await bot.send_message(chat, message)


async def on_message(message):
    async with message.process():
        await send_message_to_all_users(message.body)


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        login=RABBITMQ_LOGIN,
        password=RABBITMQ_PASS
    )
    queue_name = "telegram_queue"

    # Creating channel
    channel = await connection.channel()

    # Declaring queue
    queue = await channel.declare_queue(queue_name)

    await queue.consume(on_message)
    await dp.start_polling(bot)
    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == '__main__':
    asyncio.run(main())
