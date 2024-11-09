from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import crud
from starlette import status

from app.auth.crud import is_user_admin
from app.auth.jwt import decode_access_token
from app.company.schemas import CompanyTable
from app.database import engine
from app.employee import schemas
from app.employee.schemas import Base, EmployeeTable, Employee

import logging

logger = logging.getLogger(__name__)


async def create_employee_table():
    async with engine.begin() as conn:
        await conn.run_sync(create_employee_table_sync)


def create_employee_table_sync(conn):
    Base.metadata.tables['employee'].create(conn, checkfirst=True)


async def get_employee(db: AsyncSession, employee_id: int):
    result = await db.execute(select(EmployeeTable).where(EmployeeTable.id == employee_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не верно введен ID сотрудника. "
                                                                          "Сотрудник не найден")
    return result.scalar_one_or_none()  # Возвращает одну запись или None


async def create_employee(db: AsyncSession, employee: schemas.Employee):
    try:
        # Пытаемся найти компанию по ID
        company = await db.execute(select(CompanyTable).where(CompanyTable.id == employee.company_id))
        company_exists = company.scalar_one_or_none()

        if not company_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Компания с данным ID не найдена")

        db_employee = EmployeeTable(**employee.dict())

        # Добавляем сотрудника в сессиию
        db.add(db_employee)

        # Асинхронно коммитим изменения в базе данных
        await db.commit()

        # Обновляем объект db_company данными из базы
        await db.refresh(db_employee)

        return db_employee
    except IntegrityError as e:
        await db.rollback()  # Откатываем изменения в случае ошибки
        raise HTTPException(status_code=400, detail="Ошибка при создании сотрудника") from e


async def create_test_employees(db: AsyncSession):
    # Пример данных тестовых сотрудников для каждой компании
    employees_data = [
        {"first_name": "Иван", "last_name": "Иванов", "middle_name": "Иванович", "phone": "+79001234567",
         "email": "ivan@example.com", "birthdate": date(1990, 1, 1), "company_id": 1},
        {"first_name": "Сергей", "last_name": "Петров", "middle_name": "Сергеевич", "phone": "+79007654321",
         "email": "sergei@example.com", "birthdate": date(1985, 5, 15), "company_id": 1},
        {"first_name": "Анна", "last_name": "Сидорова", "middle_name": "Анатольевна", "phone": "+79009876543",
         "email": "anna@example.com", "birthdate": date(1992, 3, 20), "company_id": 2},
        {"first_name": "Дмитрий", "last_name": "Николаев", "middle_name": "Дмитриевич", "phone": "+79005432123",
         "email": "dmitry@example.com", "birthdate": date(1988, 7, 30), "company_id": 2},
        {"first_name": "Елена", "last_name": "Кузнецова", "middle_name": "Викторовна", "phone": "+79006789012",
         "email": "elena@example.com", "birthdate": date(1995, 11, 10), "company_id": 3},
        {"first_name": "Максим", "last_name": "Федоров", "middle_name": "Максимович", "phone": "+79001234568",
         "email": "maksim@example.com", "birthdate": date(1986, 9, 25), "company_id": 3},
    ]
    for employee in employees_data:
        employee_schema = Employee(**employee)
        await create_employee(db, employee_schema)


# async def update_employee(db: AsyncSession,
#                           employee_id: int,
#                           update_data: schemas.UpdateEmployeeDto,
#                           client_token: str):
#     try:
#         # Декодирование токена и проверка роли
#         decode = await decode_access_token(client_token)
#
#         # Проверяем роль пользователя
#         if decode["user_role"] != "admin":
#             logging.error("Доступ запрещен: пользователь не является администратором.")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Доступ запрещен: только администраторы могут выполнять это действие."
#             )
#         # Пытаемся найти сотрудника по ID
#         result = await db.execute(
#             select(EmployeeTable).filter(EmployeeTable.id == employee_id)
#         )
#         db_employee = result.scalars().first()
#
#         if not db_employee:
#             raise HTTPException(status_code=404, detail="Сотрудник не найден")
#
#         # Обновляем поля, которые были переданы в update_data
#         for key, value in update_data.dict(exclude_unset=True).items():
#             setattr(db_employee, key, value)
#
#         # Асинхронно коммитим изменения в базе данных
#         await db.commit()
#
#         # Обновляем объект db_employee данными из базы
#         await db.refresh(db_employee)
#
#         return db_employee
#     except IntegrityError as e:
#         await db.rollback()  # Откатываем изменения в случае ошибки
#         raise HTTPException(status_code=400, detail="Ошибка при обновлении сотрудника") from e

async def update_employee(db: AsyncSession,
                          employee_id: int,
                          update_data: schemas.UpdateEmployeeDto,
                          client_token: str):
    try:
        # Декодирование токена и проверка роли
        await is_user_admin(client_token)

        # Пытаемся найти сотрудника по ID
        result = await db.execute(
            select(EmployeeTable).filter(EmployeeTable.id == employee_id)
        )
        db_employee = result.scalars().first()

        if not db_employee:
            raise HTTPException(status_code=404, detail="Сотрудник не найден")

        # Обновляем поля, которые были переданы в update_data
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(db_employee, key, value)

        # Асинхронно коммитим изменения в базе данных
        await db.commit()

        # Обновляем объект db_employee данными из базы
        await db.refresh(db_employee)

        return db_employee
    except IntegrityError as e:
        await db.rollback()  # Откатываем изменения в случае ошибки
        raise HTTPException(status_code=400, detail="Ошибка при обновлении сотрудника") from e


async def get_employees(db: AsyncSession, company_id: int):
    # Пытаемся найти компанию по ID
    company = await db.execute(select(CompanyTable).where(CompanyTable.id == company_id))
    company_exists = company.scalar_one_or_none()
    if not company_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Компания с данным ID не найдена")

    result = await db.execute(select(EmployeeTable).where(EmployeeTable.company_id == company_id))
    employees = result.scalars().all()  # Получаем все записи сотрудников для данной компании
    if not employees:  # Проверяем, есть ли сотрудники
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудники не найдены для данной компании.")
    logger.info(f"Retrieved {len(employees)} employees for company ID {company_id}")  # Отладочная информация
    return employees

#
# def delete_all(db: Session):
#     db.query(models.Company).delete()
#     db.query(models.Employee).delete()
#     db.query(models.Service).delete()
#     db.query(models.User).delete()
#     db.commit()
#
#