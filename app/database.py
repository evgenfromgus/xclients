from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()  # Загружаем переменные окружения из .env файла

DB_URI = os.getenv("DB_URI")

# DB_URI = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://qa:skyqa@localhost:5433/x_clients"

engine = create_async_engine(DB_URI, echo=True, future=True)
# Используем async_session maker
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    """Функция для получения асинхронной сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
