from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import (Column, Integer, String, Boolean,
                        DateTime, func)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CompanyTable(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    change_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(300))
    deleted_at = Column(DateTime(timezone=True))


class Company(BaseModel):
    name: str = Field(..., description="Название компании")
    description: Optional[str] = Field(None, description="Слоган или описание")
    is_active: bool = Field(default=True, description="Статус компании. false = неактивна.")


class CreateCompanyDto(BaseModel):
    id: int
    name: str = Field(..., description="Название компании")
    description: Optional[str] = Field(None, description="Слоган или описание")
    is_active: bool


class DeleteCompanyDto(BaseModel):
    detail: str
    company_id: int


class UpdateCompanyStatusDto(BaseModel):
    is_active: bool = Field(default=True, description="Статус компании. false = неактивна.")


class UpdateCompanyDto(BaseModel):
    name: Optional[str] = Field(None, description="Название компании")
    description: Optional[str] = Field(None, description="Слоган или описание")
