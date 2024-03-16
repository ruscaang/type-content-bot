# Module for handlers that process messages unrelated to the user's interaction with the bot.

import sys
from aiogram import Bot, F, Router
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.filters import Command
from utils import log_entry
from config_reader import config

router = Router()

react_vacancies = ReactionTypeEmoji(emoji="🕊")
react_memes = ReactionTypeEmoji(emoji="🤡")
react_files = ReactionTypeEmoji(emoji="🍓")
react_papers = ReactionTypeEmoji(emoji="🏆")
react_courses = ReactionTypeEmoji(emoji="⚡")

ORIGIN = int(config.ORIGIN.get_secret_value())
ARCHIVE = int(config.ARCHIVE.get_secret_value())
VACANCIES = int(config.VACANCIES.get_secret_value())
MEMES = int(config.MEMES.get_secret_value())
FILES = int(config.FILES.get_secret_value())
PAPERS = int(config.PAPERS.get_secret_value())
COURSES = int(config.COURSES.get_secret_value())


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("This bot is intended for personal purposes and is not public")


@router.message(Command("stop"))
async def cmd_stop(message: Message):
    await message.answer("I will be back ту-ту-ту-ту *музыка из терминатора*")
    sys.exit(0)


@router.message(Command("chat_id"))
async def cmd_chatid(message: Message):
    await message.answer(str(message.chat.id) + "_" + str(message.message_thread_id))


# @router.message(F.chat.id == ORIGIN) # function to see what is coming in the message
# async def books(message: Message):
#     print(message.model_dump_json())


# forwards files from the chat
@router.message((F.chat.id == ORIGIN) & F.document)
async def files(message: Message):
    ext_count = 0
    ext_list = ["gif", "mp3", "mp4", "png", "jpg", "jpeg", "txt", "json"]
    for ext in ext_list:
        if ext in message.document.file_name:
            ext_count += 1
    if ext_count == 0:
        await message.react([react_files])
        await message.forward(chat_id=ARCHIVE, message_thread_id=FILES)
        await log_entry(message, "files")


# forwards memes from the specified groups
@router.message(
    (F.chat.id == ORIGIN)
    & (
        F.forward_origin.chat.id.in_(
            {-1001595506698, -1001081170974, -1001009232144, -1001399874898}
        )
    )
)
async def memes(message: Message):
    await message.react([react_memes])
    await message.forward(chat_id=ARCHIVE, message_thread_id=MEMES)
    await log_entry(message, "memes")


# forwards vacancies with at least 3 keywords
@router.message((F.chat.id == ORIGIN) & F.forward_origin)
async def vacansies(message: Message):
    words_list = [
        "ищем",
        "вакансия",
        "junior",
        "middle",
        "senior",
        "компания",
        "зарплата",
        "задач",
        "python",
        "sql",
        "data",
        "аналитик",
        "ab",
        "a/b",
        "ml",
        "инженер",
    ]
    words_found_count = 0

    for word in words_list:
        if word in str.lower(message.text):
            words_found_count += 1

    if words_found_count >= 3:
        await message.react([react_vacancies])
        await message.forward(chat_id=ARCHIVE, message_thread_id=VACANCIES)
        await log_entry(message, "vacancies")


# forwards articles and courses
@router.message((F.chat.id == ORIGIN) & F.text)
async def papers(message: Message):
    data = {
        "url": None,
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract_from(message.text)
    if data["url"] is not None and "курс" not in str.lower(message.text):
        await message.react([react_papers])
        await message.forward(chat_id=ARCHIVE, message_thread_id=PAPERS)
        await log_entry(message, "papers")
    elif data["url"] is not None and "курс" in str.lower(message.text):
        await message.react([react_courses])
        await message.forward(chat_id=ARCHIVE, message_thread_id=COURSES)
        await log_entry(message, "courses")
    else:
        await log_entry(message, "other")
