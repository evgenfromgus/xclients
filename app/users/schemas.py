from enum import Enum
from pydantic import BaseModel
from sqlalchemy import (Column, Integer, String, Boolean,
                        DateTime, func, Enum as SAEnum)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RoleEnum(str, Enum):
    admin = "admin"
    client = "client"


class User(BaseModel):
    username: str
    password: str
    role: RoleEnum


"nullable = False - не может быть пустым"


class UserTable(Base):
    __tablename__ = 'app_users'
    id = Column(Integer, primary_key=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    change_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    login = Column(String(20), nullable=False)
    password = Column(String(100), nullable=False)
    display_name = Column(String(40), nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
