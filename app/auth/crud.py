import json
import logging

import redis
from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.jwt import create_access_token, decode_access_token
from app.auth.schemas import AuthRequest, AuthResponse
from app.database import get_db
from app.users.schemas import UserTable
from app.utils.radis import get_redis

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/auth/login",
             tags=["auth"],
             summary="Получение токена",
             description="Полученный токен необходимо использовать для дальнейшей работы сервиса."
                         "Токен может получить только заведенный в систему пользователь.",
             status_code=status.HTTP_200_OK,
             response_model=AuthResponse,
             responses={
                 200: {"description": "Успешная аутентификация"},
                 401: {
                     "description": "Неверный логин или пароль",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Неверный логин или пароль"
                             }
                         }
                     }
                 },
                 422: {
                     "description": "Ошибка валидации",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": [
                                     {
                                         "loc": ["body", "username"],
                                         "msg": "field required",
                                         "type": "value_error.missing"
                                     }
                                 ]
                             }
                         }
                     }
                 }
             })
async def auth_login(auth_request: AuthRequest, db: AsyncSession = Depends(get_db)):
    redis = await get_redis()
    # Создаем запрос к базе данных
    query = select(UserTable).where(UserTable.login == auth_request.username)
    result = await db.execute(query)

    # Извлекаем пользователя из результата
    user = result.scalars().first()

    # Проверяем, существует ли пользователь и соответствует ли пароль
    if not user or not pwd_context.verify(auth_request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверный логин или пароль")

    # Создание access token
    access_token = create_access_token(data={"sub": user.login, "role": user.role})

    # Сохраняем токен в Redis с временем жизни, например, 1 час (3600 секунд)
    await redis.set(f"user_token:{user.login}", access_token, ex=3600)

    return AuthResponse(
        user_token=access_token,
        role=user.role,
        display_name=user.display_name,
    )


async def get_token_from_redis(login: str, redis_token: redis.Redis = Depends(get_redis)):
    """
    Функция извлечения токена из Redis по логину пользователя.
    """
    token = await redis_token.get(f"user_token:{login}")
    return token.decode("utf-8") if token else print("Token not found")


async def is_user_admin(client_token: str):
    # Декодирование токена и проверка роли
    decode = await decode_access_token(client_token)

    # Проверяем роль пользователя
    if decode["user_role"] != "admin":
        logging.error("Доступ запрещен: пользователь не является администратором.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен: только администраторы могут выполнять это действие."
        )
    return True


async def is_user_superadmin(client_token: str):
    # Декодирование токена и проверка роли
    decode = await decode_access_token(client_token)

    # Проверяем роль пользователя и имя
    if not (decode["user_role"] == "admin" and decode["user_login"] == "voldemort"):
        logging.error(f"Доступ запрещен: попытка входа с логином {decode["user_login"]} и ролью {decode["user_role"]}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Только высшие силы смогу получить доступ к этому ресурсу."
                   f"А ты {decode["user_login"]} с ролью {decode["user_role"]} пересмотри свою магическую силу."
        )
    return True
