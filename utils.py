from aiogram import types
from typing import Dict, Any

from database.db_commands import log_message
from database.db_models import create_database, create_tables


async def check_db_exists() -> None:
    """
    Check if the db file exists
    :return: None
    """
    await create_database()
    await create_tables()


async def log_entry(message: types.Message, label) -> None:
    """
    Prepares data and logs it into db tables
    :param message: types.Message containing all info from tg
    :param label: None
    :return:
    """
    user_dict = await prepare_user(message.from_user)
    message_dict = await prepare_message(message)
    await log_message(user_dict, message_dict, label)


async def prepare_user(user: Any) -> Dict:
    """
    Prepares user to log into db
    :param user: User from types.Message.from_user
    :return: dict of tg_user
    """
    user_dict = {'user_id': user.id or '',
                 'username': user.username or '',
                 'first_name': user.first_name or '',
                 'last_name': user.last_name or ''}
    return user_dict


async def prepare_message(message: types.Message) -> Dict:
    """
    Prepares message to log into db
    :param message: Message type
    :return: dict of tg_user
    """
    get_error = 0
    try:
        j_data = message.model_dump_json()
    except Exception as e:  # PydanticSerializationError
        print("Couldn't log json", str(e))
        j_data = str(message.model_dump())
        get_error = 1

    message_dict = {'message_id': message.message_id or '',
                    'text_data': message.text or '',
                    'json_data':  j_data,
                    'get_error': get_error}
    return message_dict


async def log_and_forward(bot: Any, message: types.Message,
                          target_chat: int, label_name: str,
                          sub_chats: Dict, reactions: Dict) -> None:
    """
    Utility function to forward message, log message in db and send a reaction.
    :param bot: Bot dispatcher instance
    :param message: Message type of aiogram
    :param target_chat: Int address of chat to forward message to
    :param label_name: String to use as a reference for a label
    :param sub_chats: Dict of all sub chats
    :param reactions: Dict of all reactions
    :return:
    """
    await bot.forward_message(chat_id=target_chat, from_chat_id=message.chat.id,
                              message_id=message.message_id, message_thread_id=sub_chats[label_name])
    await log_entry(message, label_name)
    await message.react([reactions[label_name]])
