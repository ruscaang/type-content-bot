import asyncio
from aiogram import types

from typing import Dict, Any

from database.db_commands import log_message
from database.db_models import create_tables, async_engine


def check_db_exists() -> None:
    """
    Check if the db file exists
    :return:
    """
    asyncio.run(create_tables(async_engine))


async def log_entry(message: types.Message, label) -> None:
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
    message_dict = {'message_id': message.message_id or '',
                    'text_data': message.text or '',
                    'json_data': message.model_dump_json() or ''}
    return message_dict
