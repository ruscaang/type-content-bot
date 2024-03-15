import asyncpg
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config_reader import config


DEFAULT_DB_NAME = config.DEFAULT_DB_NAME.get_secret_value()
DB_USER = config.DB_USER.get_secret_value()
DB_PASSWORD = config.DB_PASSWORD.get_secret_value()
DB_HOST = config.DB_HOST.get_secret_value()
DB_PORT = config.DB_PORT.get_secret_value()
DB_NAME = config.DB_NAME.get_secret_value()

#  DATABASE_URL = "sqlite+aiosqlite:///database/content_bot.db"
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()
async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_factory = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_connect(db_name: str = DB_NAME):
    """
    Connects to db and returns connection

    :param db_name: name of a database to connect to
    :return:
    """
    return await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=db_name, host=DB_HOST, port=DB_PORT)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(Integer, unique=True)

    info = relationship("UserInfo", back_populates="user", uselist=False)
    messages = relationship("Message", back_populates="user")


class UserInfo(Base):
    __tablename__ = 'user_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)

    user = relationship("User", back_populates="info", uselist=False)


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tg_message_id = Column(Integer, unique=True)
    label = Column(String)
    text_data = Column(Text)
    json_data = Column(Text)
    get_error = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="messages")


async def create_database() -> None:
    """
    Create db if it doesn't exist

    :return: None
    """
    conn = await get_connect(db_name=DEFAULT_DB_NAME)    # Check if the target database exists
    db_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=$1)", DB_NAME)
    if not db_exists:
        await conn.close()
        # connection to default db to create a new db
        conn = await get_connect(db_name=DEFAULT_DB_NAME)
        await conn.execute(f'CREATE DATABASE {DB_NAME}')
        print(f"Database '{DB_NAME}' created.")
    else:
        print(f"Database '{DB_NAME}' already exists.")
    await conn.close()


async def create_tables() -> None:
    """
    Create tables in the db if they don`t exist

    :return: None
    """
    try:
        async with async_engine.begin() as conn:
            # Create tables
            #  await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully")
    except asyncpg.exceptions.PostgresError as e:
        print(f"Error creating tables: {e}")


# if __name__ == "__main__":
    # import asyncio
    # asyncio.run(create_database())
    # asyncio.run(create_tables(async_engine))
