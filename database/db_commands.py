from database.db_models import User, UserInfo, Message, MessageTextData, MessageJSONData, \
                               async_session_factory
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound


async def log_message(tg_user, tg_message, label):
    await create_or_update_user(tg_user['user_id'], tg_user['username'], tg_user['first_name'], tg_user['last_name'])
    await insert_message(tg_user['user_id'], tg_message['message_id'], tg_message['text_data'], tg_message['json_data'],
                         label)


async def create_or_update_user(tg_user_id, username=None, first_name=None, last_name=None) -> None:
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


async def insert_message(tg_user_id, tg_message_id, text_data, json_data, label):
    async with async_session_factory() as session:
        statement = select(User).where(User.tg_user_id == tg_user_id)
        result = await session.execute(statement)
        user = result.scalar_one()

        new_message = Message(user_id=user.id,
                              tg_message_id=tg_message_id,
                              text_data=[MessageTextData(text_data=text_data)],
                              json_data=[MessageJSONData(json_data=json_data)],
                              label=label)
        session.add(new_message)
        await session.commit()


async def update_message_by_id(tg_message_id, new_label):
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


async def fetch_data_by_user_id(tg_user_id):
    async with async_session_factory() as session:
        result = await session.execute(
            select(User)
            .where(User.tg_user_id == tg_user_id)
            .options(
                joinedload(User.info),
                joinedload(User.messages).joinedload(Message.text_data)
            )
        )
        user = result.scalars().first()

        if not user:
            return "User not found."

        # Extract user information
        username = user.info.username if user.info else "No Username"
        first_name = user.info.first_name if user.info else "No First Name"
        last_name = user.info.last_name if user.info else "No Last Name"

        messages_info = []
        for message in user.messages:
            label_name = message.label if message.label else "No Label"
            message_text = message.text_data[0].text_data if message.text_data else "No Text"
            message_info = f"Message ID: {message.tg_message_id}\nLabel: {label_name}\nText: {message_text}\n"
            messages_info.append(message_info)

        user_info = f"User: {user.tg_user_id} {username}\n" \
                    f"Name: {first_name} {last_name}\n" \
                    f"\nMessages:\n" + "\n".join(messages_info)
        return user_info
