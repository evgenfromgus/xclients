from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import (Column, Integer, String, Boolean,
                        DateTime, func, DATE)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EmployeeTable(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True, nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    change_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    middle_name = Column(String(20))
    phone = Column(String(15), nullable=False)
    email = Column(String(256))
    birthdate = Column(DATE)
    company_id = Column(Integer, nullable=False)


class Employee(BaseModel):

    first_name: str = Field(...,  description="Имя специалиста")
    last_name: str = Field(..., description="Фамилия специалиста")
    middle_name: Optional[str] = Field(None, description="Отчество специалиста")
    company_id: int = Field(..., description="id компании")
    email: Optional[EmailStr] = Field(None, description="Email для уведомлений")
    phone: Optional[str] = Field(None, description="Номер телефона")
    birthdate: Optional[date] = Field(None, description="Дата рождения")
    is_active: bool = Field(default=True, description="Статус сотрудника. false = неактивен.")


class UpdateEmployeeDto(BaseModel):
    last_name: Optional[str] = Field(None, description="Фамилия специалиста")
    email: Optional[EmailStr] = Field(None, description="Email для уведомлений")
    phone: Optional[str] = Field(None, description="Номер телефона")
    is_active: Optional[bool] = Field(None, description="Статус сотрудника. false = неактивен.")
