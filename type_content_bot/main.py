import asyncio
import sys
import logging
from aiogram import Bot, Dispatcher
from config_reader import config
from utils import check_db_exists
from handlers import other_handlers, user_handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()
dp.include_router(user_handlers.router)
dp.include_router(other_handlers.router)


async def main():
    await asyncio.gather(check_db_exists())
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shut down")
        sys.exit(0)
