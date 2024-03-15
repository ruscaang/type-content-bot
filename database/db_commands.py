from database.db_models import User, UserInfo, Message, async_session_factory
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from typing import Any, Dict


async def create_or_update_user(tg_user_id: int, username=None, first_name=None, last_name=None) -> None:
    """
    Create or Update User

    :param tg_user_id: User`s tg id
    :param username:  Username if it exists
    :param first_name: Name if it exists
    :param last_name:  Surname if it exists
    :return: None
    """
    async with async_session_factory() as session:
        statement = select(User).where(User.tg_user_id == tg_user_id)
        try:
            result = await session.execute(statement)
            user = result.scalar_one()
            # Update user info
            if username or first_name or last_name:
                user_info = await session.get(UserInfo, user.id)
                if user_info:
                    user_info.username = username or user_info.username
                    user_info.first_name = first_name or user_info.first_name
                    user_info.last_name = last_name or user_info.last_name
                else:
                    user.info = UserInfo(username=username, first_name=first_name, last_name=last_name)
            await session.commit()
        except NoResultFound:
            # Create new user
            new_user = User(tg_user_id=tg_user_id,
                            info=UserInfo(username=username,
                                          first_name=first_name,
                                          last_name=last_name))
            session.add(new_user)
            await session.commit()


async def insert_message(
    tg_user_id: int, tg_message_id: int, text_data: str,
    json_data: Any, get_error: int, label: str
    ) -> None:
    """
    Inserts message to Message table associating it with a user by id

    :param tg_user_id: Tg user id
    :param tg_message_id: TG message id
    :param text_data: text message
    :param json_data: dumped json data
    :param json_data: if get error for dump_json function
    :param label: message label (vacancies, articles, courses, memes, files)
    :return: None
    """
    async with async_session_factory() as session:
        statement = select(User).where(User.tg_user_id == tg_user_id)
        result = await session.execute(statement)
        user = result.scalar_one()

        new_message = Message(user_id=user.id,
                              tg_message_id=tg_message_id,
                              text_data=text_data,
                              json_data=json_data,
                              get_error=get_error,
                              label=label)
        session.add(new_message)
        await session.commit()


async def log_message(tg_user: Dict, tg_message: Dict, label: str):
    """
    Logs data into tables from prepared dicts
    :param tg_user: Dict with user data
    :param tg_message: Dict with message data
    :param label: Message label
    :return:
    """
    await create_or_update_user(tg_user['user_id'], tg_user['username'], tg_user['first_name'], tg_user['last_name'])
    await insert_message(tg_user['user_id'], tg_message['message_id'], tg_message['text_data'], tg_message['json_data'],
                         tg_message['get_error'], label)


async def update_message_by_id(tg_message_id: int, new_label: str) -> bool:
    """
    Func to change message label. Not implemented in main.py yet
    :param tg_message_id: id of the message
    :param new_label: new label
    :return:
    """
    async with async_session_factory() as session:
        # Try to find the message by its Telegram message ID
        statement = select(Message).where(Message.tg_message_id == tg_message_id)
        result = await session.execute(statement)
        message = result.scalar_one_or_none()

        if not message:
            print("Message not found")
            return False

        message.label = new_label
        await session.commit()
        return True


async def fetch_data_by_user_id(tg_user_id: int) -> str:
    """
    Function to return all user data and his messages. Later take last 10 messages
    :param tg_user_id: user tg id
    :return: user_data consists of user info and messages
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(User)
            .where(User.tg_user_id == tg_user_id)
            .options(
                joinedload(User.info),
                joinedload(User.messages)
            )
        )
        user = result.scalars().first()

        if not user:
            return "User not found."

        # Extract user information
        username = user.info.username if user.info else ""
        first_name = user.info.first_name if user.info else ""
        last_name = user.info.last_name if user.info else ""

        messages_info = []
        for message in user.messages:
            label_name = message.label or "No Label"  # Ivan asked for this
            message_text = message.text_data or "No text"
            message_info = f"Message ID: {message.tg_message_id}\nLabel: {label_name}\nText: {message_text}\n"
            messages_info.append(message_info)

        all_messages = "\n".join(messages_info)
        user_info = f"User: {user.tg_user_id} {username}\n" \
                    f"Name: {first_name} {last_name}\n" \
                    f"\nMessages:\n{all_messages}"
        return user_info
