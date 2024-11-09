from pydantic import BaseModel, Field
from enum import Enum


# Определение перечисления для ролей
class RoleEnum(str, Enum):
    admin = "admin"
    emp = "emp"
    client = "client"


# Определение схем для запросов и ответов
class AuthRequest(BaseModel):
    username: str = Field(..., description="Логин")
    password: str = Field(..., description="Пароль")


class AuthResponse(BaseModel):
    user_token: str = Field(..., description="Токен")
    role: RoleEnum = Field(..., description="Роль")
    display_name: str
    # login: str
