import asyncio
import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.metadata import metadata

# Загрузить переменные окружения из .env файла
load_dotenv()

# Получить DB_URI из переменной окружения
db_uri = os.getenv("DB_URI")
if db_uri is None:
    raise ValueError("Переменная окружения DB_URI не установлена.")

# Установить sqlalchemy.url для Alembic
context.config.set_main_option('sqlalchemy.url', db_uri)

# Настройка логирования
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Добавьте ваш объект MetaData модели здесь для поддержки 'autogenerate'
target_metadata = metadata


def run_migrations_offline() -> None:
    """Запустить миграции в 'offline' режиме."""
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """В этом сценарии необходимо создать Engine и ассоциировать соединение с контекстом."""
    connectable = async_engine_from_config(
        context.config.get_section(context.config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запустить миграции в 'online' режиме."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
