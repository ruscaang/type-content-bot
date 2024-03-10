
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

#  import asyncpg
# "postgresql+asyncpg://USERNAME:PASSWORD@localhost/content_bot_db"
DATABASE_URL = "sqlite+aiosqlite:///database/content_bot.db"

Base = declarative_base()

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_factory = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


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
    timestamp = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="messages")


async def create_database() -> None:
    """
    Necessary for solid dbs like pg

    :return: None
    """
    engine = create_async_engine(DATABASE_URL, echo=True, future=True)
    async with engine.connect() as conn:
        await conn.execute("CREATE DATABASE content_bot_db")


async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# if __name__ == "__main__":
    # import asyncio
    # asyncio.run(create_database())
    # asyncio.run(create_tables(async_engine))
