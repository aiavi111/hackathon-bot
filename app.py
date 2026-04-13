import asyncio
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

router = Router()

@router.message()
async def show_chat_id(message: Message):
    print("CHAT ID:", message.chat.id)
    await message.answer(f"CHAT ID: {message.chat.id}")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())