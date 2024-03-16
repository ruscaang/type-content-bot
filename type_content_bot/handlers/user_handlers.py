# Module for handlers that process messages related to the user's interaction with the bot.

from aiogram import Router
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.filters import Command
from database.db_commands import fetch_data_by_user_id, update_message_by_id

react_label = ReactionTypeEmoji(emoji="✍")
router = Router()


@router.message(Command("getme"))
async def cmd_get_my_messages(message: Message):
    """
    Get all your messages
    :param message:
    :return:
    """
    result = await fetch_data_by_user_id(message.from_user.id)
    await message.answer(result)


@router.message(Command("label"))
async def change_label(message: Message):
    labels = ["memes", "vacancies", "files", "courses", "papers", "other"]
    if len(message.text.split(" ")) > 1:
        label = message.text.split(" ")[1]
        if message.reply_to_message is not None and label in labels:
            await update_message_by_id(message.reply_to_message.message_id, label)
            await message.react([react_label])
        else:
            await message.answer("Нет такого лейбла или нет реплая на сообщение")
    else:
        await message.answer("Не передан новый лейбл")


@router.message(Command("label_info"))
async def change_label_info(message: Message):
    await message.answer(
        """
    С помощью команды label можно сменить размеченный лейбл у сообщения. 
Для этого отправьте команду и новый лейбл через пробел.
В данный момент можно указать для сообщения следующие лейблы:
memes, files, vacancies, papers, courses, other
    """
    )
