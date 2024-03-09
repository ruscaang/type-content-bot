import asyncio
from sqlalchemy.future import select

from db_commands import store_user_content, async_session_factory
from db_models import Base, User, Message, async_engine


class MockUser:
    def __init__(self, user_id, username, first_name, last_name):
        self.id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


async def main() -> None:
    """
    Define mock users as if they were coming from aiogram

    :return: None
    """
    mock_users = {
        1: MockUser(1, "user1", "User", "One"),
        2: MockUser(2, "user2", "User", "Two"),
        3: MockUser(3, "user3", "User", "Three"),
    }

    # Define user messages and types
    users_messages = [
        (1, "message", "Hello from user 1!"),
        (2, "message", "Hello from user 2!"),
        (1, "article", "Here is the article. http://example.com/article1"),
        (3, "message", "Hello from user 3!"),
        (2, "vacancy", "I've posted a vacancy."),
        (3, "course", "Great course http://example.com/course3")]

    for user_id, content_type, text_data in users_messages:
        mock_user = mock_users[user_id]
        await store_user_content(mock_user, text_data, content_type)


async def fetch_user_to_print(tg_user_id: int):
    async with async_session_factory() as session:
        # Fetch user by Telegram user ID
        user_result = await session.execute(select(User).filter_by(tg_user_id=tg_user_id))
        user = user_result.scalars().first()

        if not user:
            print(f"\nNo user found with Telegram user ID: {tg_user_id}\n\n")
            return

        combined_entries = f"\nEntries for user {user.id} (TG User ID: {tg_user_id}):\n"

        # Define a list of model and section names
        models_sections = [
            (Message, "Messages")
        ]

        for model, section_name in models_sections:
            combined_entries += f"\n{section_name}:\n"
            entries = await session.execute(select(model).filter_by(user_id=user.id))
            entries = entries.scalars().all()
            if entries:
                for entry in entries:
                    combined_entries += f"- {entry.text_data} at {entry.timestamp}\n\n"
            else:
                combined_entries += "No entries found.\n\n"

        print(combined_entries)

if __name__ == "__main__":
    # asyncio.run(create_database())
    #asyncio.run(Base.metadata.create_all(async_engine))
    for n in range(4):
        asyncio.run(fetch_user_to_print(n))

