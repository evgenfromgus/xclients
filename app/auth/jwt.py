import logging
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException
from starlette import status

logging.basicConfig(level=logging.INFO)

# Загружаем переменные окружения
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

# Проверяем, установлен ли SECRET_KEY
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables.")


def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # Убедитесь, что 'exp' является целым числом
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logging.info(f"Токен без декодирования создан: {encoded_jwt}")
    return encoded_jwt


async def decode_access_token(token: str):
    try:
        logging.info(f"Декодирование токена: {token}")

        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Извлекаем логин пользователя из payload
        user_login = payload.get("sub")
        # Извлекаем роль пользователя из payload
        user_role = payload.get("role")
        # Извлекаем срок действия токена пользователя из payload
        token_expire = payload.get("exp")

        # Проверка на наличие роли
        if user_role is None:
            logging.error("Роль пользователя отсутствует в токене")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Роль пользователя не найдена"
            )

        # Возвращаем словарь с информацией
        decoded_info = {
            "user_login": user_login,
            "user_role": user_role,
            "token_expire": token_expire
        }

        return decoded_info

    except jwt.ExpiredSignatureError:
        logging.error("Токен истек")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек"
        )

    except jwt.InvalidTokenError:
        logging.error("Неверный токен")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )

    except KeyError as e:
        logging.error(f"Ошибка decrypted payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при декодировании токена"
        )