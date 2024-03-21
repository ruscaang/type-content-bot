import asyncio
import sys
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config
from aiogram import F

from utils import log_entry, check_db_exists, log_and_forward
from database.db_commands import fetch_data_by_user_id, update_message_by_id


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()

REACTIONS = {
    'vacancies': types.ReactionTypeEmoji(emoji="🕊"),
    "memes": types.ReactionTypeEmoji(emoji="🤡"),
    "files": types.ReactionTypeEmoji(emoji="🍓"),
    "papers": types.ReactionTypeEmoji(emoji="🏆"),
    "courses": types.ReactionTypeEmoji(emoji="⚡"),
    "label": types.ReactionTypeEmoji(emoji="✍"),
}

SUB_CHATS = {
    'vacancies': int(config.VACANCIES.get_secret_value()),
    'memes': int(config.MEMES.get_secret_value()),
    'files': int(config.FILES.get_secret_value()),
    'papers': int(config.PAPERS.get_secret_value()),
    'courses': int(config.COURSES.get_secret_value())
    }

ORIGIN = int(config.ORIGIN.get_secret_value())
ARCHIVE = int(config.ARCHIVE.get_secret_value())


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("This bot is intended for personal purposes and is not public")


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    await message.answer("I will be back ту-ту-ту-ту *музыка из терминатора*")
    sys.exit(0)


@dp.message(Command("getme"))
async def cmd_get_my_messages(message: types.Message):
    """
    Get all your messages
    :param message:
    :return:
    """
    result = await fetch_data_by_user_id(message.from_user.id)
    await message.answer(result)


@dp.message(Command("chat_id"))
async def cmd_chatid(message: types.Message):
    await message.answer(str(message.chat.id) + "_" + str(message.message_thread_id))


@dp.message(Command("label"))
async def change_label(message: types.Message):
    labels = ["memes", "vacancies", "files", "courses", "papers", "other"]
    if len(message.text.split(' ')) > 1:
        label = message.text.split(' ')[1]
        if message.reply_to_message is None:
            await bot.send_message(ORIGIN, "Нет реплая на сообщение")
        elif label in labels:
            await update_message_by_id(message.reply_to_message.message_id, label)
            await bot.forward_message(ARCHIVE, message.chat.id, message.reply_to_message.message_id,
                                      message_thread_id=SUB_CHATS[label])
            await message.react([REACTIONS['label']])
        else:
            await bot.send_message(ORIGIN, "Нет такого лейбла")
    else:
        await bot.send_message(ORIGIN, "Не передан новый лейбл")


@dp.message(Command("label_info"))
async def change_label_info(message: types.Message):
    await bot.send_message(ORIGIN, """
    С помощью команды label можно сменить размеченный лейбл у сообщения. 
Для этого отправьте команду и новый лейбл через пробел.
В данный момент можно указать для сообщения следующие лейблы:
memes, files, vacancies, papers, courses, other
    """)


# @dp.message(F.chat.id == ORIGIN) # function to see what is coming in the message
# async def books(message: types.Message):
#     print(message.model_dump_json())


# forwards files from the chat
@dp.message((F.chat.id == ORIGIN) & (F.document))
async def files(message: types.Message):
    ext_count = 0
    ignore_list = ["gif", "mp3", "mp4", "png", "jpg", "jpeg", "txt", "json"]
    for ext in ignore_list:
        if ext in message.document.file_name:
            ext_count += 1
    if ext_count == 0:

        await log_and_forward(bot, message, target_chat=ARCHIVE, chat_label=SUB_CHATS['files'],
                              db_label='files', reaction=REACTIONS['files'])


# forwards memes from the specified groups
@dp.message((F.chat.id == ORIGIN) & (F.forward_origin.chat.id.in_({-1001595506698, -1001081170974,
                                                                   -1001009232144, -1001399874898})))
async def memes(message: types.Message):
    await log_and_forward(bot, message, target_chat=ARCHIVE, chat_label=SUB_CHATS['memes'],
                          db_label='memes', reaction=REACTIONS['memes'])


# forwards vacancies with at least 3 keywords
@dp.message((F.chat.id == ORIGIN) & (F.forward_origin))
async def vacancies(message: types.Message):
    words_list = ["ищем", "вакансия", "junior", "middle", "senior", "компания", "зарплата", "задач", "python", 
                  "sql", "data", "аналитик", "ab", "a/b", "ml", "инженер"]
    words_found_count = 0
    
    for word in words_list:
        if word in str.lower(message.text):
            words_found_count += 1
        
    if words_found_count >= 3:
        await log_and_forward(bot, message, target_chat=ARCHIVE, chat_label=SUB_CHATS['vacancies'],
                              db_label='vacancies', reaction=REACTIONS['vacancies'])


# forwards articles and courses
@dp.message((F.chat.id == ORIGIN) & (F.text))
async def papers(message: types.Message):
    data = {
        "url": None,
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract_from(message.text)
    if data["url"] is not None and "курс" not in str.lower(message.text):

        await log_and_forward(bot, message, target_chat=ARCHIVE, chat_label=SUB_CHATS['papers'],
                              db_label='papers', reaction=REACTIONS['papers'])

    elif data["url"] is not None and "курс" in str.lower(message.text):
        await log_and_forward(bot, message, target_chat=ARCHIVE, chat_label=SUB_CHATS['courses'],
                              db_label='courses', reaction=REACTIONS['courses'])

    else:
        await log_entry(message, 'other')
       

async def main():
    await asyncio.gather(check_db_exists())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shut down")
        sys.exit(0)
