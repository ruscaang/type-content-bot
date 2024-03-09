import asyncio
import yaml
import json

from aiogram.types import Message
from pathlib import Path
from typing import Dict, Any

from database.db_models import create_tables, async_engine
from database.db_commands import log_message


def check_db_exists(db_path: str = 'database/content_bot.db') -> None:
    """
    Check if the db file exists
    :param db_path: db address
    :return:
    """
    db_file_path = Path(db_path)
    if not db_file_path.exists():
        asyncio.run(create_tables(async_engine))


def get_yaml(filename: str = 'config.yaml'):
    """
    Reads the configuration file.

    :return: values from config
    """
    with open(filename, 'r') as f:
        config = yaml.safe_load(f)
    return config


def get_json(filename: str = 'chat_ids.json'):
    """
    Load data from JSON file

    :param filename: Name of the file to load
    :return: values forn json
    """
    with open(filename, "r") as file:
        result = json.load(file)
    return result


async def log_entry(message: Message, label) -> None:
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


async def prepare_message(message: Message) -> Dict:
    """
    Prepares message to log into db
    :param message: Message type
    :return: dict of tg_user
    """
    message_dict = {'message_id': message.message_id or '',
                    'text_data': message.text or '',
                    'json_data': message.model_dump_json() or ''}
    return message_dict
