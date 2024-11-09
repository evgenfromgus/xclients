import logging

import redis
from dotenv import load_dotenv
from redis.exceptions import ConnectionError
from redis.asyncio import Redis
import os

load_dotenv()  # Загружаем переменные окружения из .env файла

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_instance = None


async def init_redis():
    global redis_instance
    try:
        logger.info("Инициализация подключения к Redis...")
        redis_instance = Redis(host=REDIS_HOST, port=int(REDIS_PORT))
        await redis_instance.ping()  # Проверка соединения с Redis
        logger.info("Подключение к Redis успешно установлено.")
    except ConnectionError as e:
        logger.error("Ошибка подключения к Redis: %s", e)


async def get_redis():
    global redis_instance
    if redis_instance is None:  # Использование сравнения с None
        await init_redis()
    else:
        logger.info("Используется существующее подключение к Redis.")
    return redis_instance


async def close_redis():
    global redis_instance
    if redis_instance is not None:  # Дополнительная проверка на None
        logger.info("Закрытие соединения с Redis...")
        await redis_instance.close()
        redis_instance = None  # Установка в None после закрытия соединения
        logger.info("Соединение с Redis закрыто.")
    else:
        logger.warning("Попытка закрыть соединение с Redis, но оно уже не открыто.")


async def save_decoded_token_to_redis(user_login: str, decoded_data: dict, redis_client: redis.Redis):
    """
    Сохранение декодированных данных токена в Redis.
    """
    await redis_client.set(f"decoded_user:{user_login}", str(decoded_data))
