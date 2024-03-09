import asyncio
import sys
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config
from aiogram import F
from aiogram.types import InputFile
from utils import get_json, get_yaml, check_db_exists, log_entry
from database.db_commands import fetch_data_by_user_id, update_message_by_id


check_db_exists('database/content_bot.db')

CHATS = get_json('chat_ids.json')
ORIGIN = CHATS['origin']
ARCHIVE = CHATS['archive']
LABELS = get_yaml('labels.yaml')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()
react = types.ReactionTypeEmoji(emoji="✍")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("This bot is intended for personal purposes and is not public")


@dp.message(Command("stop"))
async def cmd_start(message: types.Message):
    await message.answer("I will be back ту-ту-ту-ту *музыка из терминатора*")
    sys.exit(1)


@dp.message(Command("getme"))
async def cmd_start(message: types.Message):
    result = await fetch_data_by_user_id(message.from_user.id) or 'hi'
    await message.answer(result)


@dp.message(Command("chat_id"))
async def cmd_chatid(message: types.Message):
    await message.answer(str(message.chat.id) + "_" + str(message.message_thread_id))

# пересылает файлы из чата


@dp.message((F.chat.id == ORIGIN) & (F.document))
async def files(message: types.Message):
    ext_count = 0
    ext_list = ["gif", "mp3", "mp4", "png", "jpg", "jpeg", "txt", "json"]
    for ext in ext_list:
        if ext in message.document.file_name:
            ext_count += 1
    if ext_count == 0:
        await message.react([react])
        await bot.send_message(ARCHIVE, message.from_user.username, message_thread_id=CHATS['files'])
        await bot.send_document(ARCHIVE, document=message.document.file_id, message_thread_id=CHATS['files'])
        await log_entry(message, LABELS[5])

# пересылает мемы из указанных групп


@dp.message((F.chat.id == ORIGIN) & (F.forward_origin.chat.id.in_(CHATS["meme_chats"])))
async def memes(message: types.Message):
    await message.react([react])
    await bot.forward_message(ARCHIVE, message.chat.id, message.message_id, message_thread_id=CHATS['memes'])
    await log_entry(message, LABELS[4])

# пересылает вакансии в которых есть от 3 ключевых слов


@dp.message((F.chat.id == ORIGIN) & (F.forward_origin))
async def vacancies(message: types.Message):
    words_list = ["ищем", "вакансия", "junior", "middle", "senior", "компания", "зарплата",
                  "задач", "python", "sql", "data", "аналитик", "ab", "a/b", "ml", "инженер"]
    words_found_count = 0
    
    for word in words_list:
        if word in str.lower(message.text):
            words_found_count += 1
        
    if words_found_count >= 3:
        await message.react([react])
        await bot.forward_message(ARCHIVE, message.chat.id, message.message_id, message_thread_id=CHATS['vacancies'])
        await log_entry(message, LABELS[2])


# пересылает статьи и курсы
@dp.message((F.chat.id == ORIGIN) & (F.text))
async def papers(message: types.Message):
    data = {"url": None}
    entities = message.entities or []

    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract_from(message.text)

    if data["url"] is not None and "курс" not in str.lower(message.text):
        await message.react([react])
        await bot.send_message(ARCHIVE, message.from_user.username + ": " + data["url"],
                               message_thread_id=CHATS['articles'])
        await log_entry(message, LABELS[3])

    elif data["url"] is not None and "курс" in str.lower(message.text):
        await message.react([react])
        await bot.send_message(ARCHIVE, message.from_user.username + "\n" + message.text,
                               message_thread_id=CHATS['courses'])
        await log_entry(message, LABELS[6])
    else:
        await log_entry(message, LABELS[7])


'''
@dp.message(F.chat.id == ORIGIN)  # функция чтобы увидеть что приходит в сообщении
async def books(message: types.Message):
    print(message.model_dump_json())
'''


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
