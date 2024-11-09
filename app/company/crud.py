from typing import Dict

from fastapi import HTTPException
from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from typing_extensions import Optional
import logging

from app.auth.crud import is_user_admin
from app.auth.jwt import decode_access_token
from app.company.schemas import Base, CompanyTable, Company, UpdateCompanyDto
from app.database import engine
from app.employee.schemas import EmployeeTable

logger = logging.getLogger(__name__)


async def create_company_table():
    async with engine.begin() as conn:
        await conn.run_sync(create_company_table_sync)


def create_company_table_sync(conn):
    Base.metadata.tables['company'].create(conn, checkfirst=True)


async def create_test_companies(db: AsyncSession):
    # Очистка таблицы пользователей и компаний
    await db.execute(text("TRUNCATE TABLE employee RESTART IDENTITY"))
    # await db.execute(delete(EmployeeTable))
    await db.execute(text("TRUNCATE TABLE company RESTART IDENTITY"))  # Очистка таблицы company чтобы ID начинался с 1
    # await db.execute(delete(CompanyTable))
    await db.commit()

    # Список тестовых компаний
    companies = [
        CompanyTable(name="QA Студия 'ТестировщикЪ'", description='Качественное тестирование для успешных проектов'),
        CompanyTable(name='Автоматизация тестирования',
                     description='Эффективные решения для автоматизации процессов QA'),
        CompanyTable(name='Курсы по тестированию ПО', description='Обучение современным методам тестирования и QA'),
        CompanyTable(name="Консалтинговая компания 'QA-Эксперт'",
                     description='Экспертиза и аудит качества программного обеспечения'),
        CompanyTable(name='Служба поддержки QA', description='Помощь и поддержка в вопросах тестирования',
                     is_active=False),
    ]

    db.add_all(companies)
    await db.commit()


async def create_company(db: AsyncSession, company_data: Company):
    # Создаем объект компании
    db_company = CompanyTable(**company_data.dict())

    # Добавляем компанию в сессию
    db.add(db_company)

    try:
        # Асинхронно коммитим изменения в базе данных
        await db.commit()

        # Обновляем объект db_company данными из базы
        await db.refresh(db_company)

        return db_company
    except IntegrityError as e:
        await db.rollback()  # Откатываем изменения в случае ошибки
        raise HTTPException(status_code=400, detail="Ошибка при создании компании") from e


async def get_companies(db: AsyncSession, active_only: Optional[bool] = None):
    try:
        query = select(CompanyTable)
        if active_only is not None:  # Проверяем, передан ли параметр
            query = query.where(CompanyTable.is_active == active_only)

        result = await db.execute(query)
        companies = result.scalars().all()

        return companies
    except HTTPException as e:
        if e.status_code == 401:
            return {"error": "Неверные данные запроса"}
        elif e.status_code == 422:
            return {"error": "Ошибка валидации", "details": e.detail}
        else:
            return {"error": "Внутренняя ошибка сервера"}


async def get_company(db: AsyncSession, company_id: int):
    # Создаем запрос, используя future API
    query = select(CompanyTable).where(CompanyTable.id == company_id)
    result = await db.execute(query)  # Выполняем запрос асинхронно
    db_company = result.scalar()
    if not db_company:
        logger.warning(f"Компания с ID {company_id} не найдена")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Компания не найдена")

    return db_company


async def update_company_data(db: AsyncSession, company_id: int, company_data: UpdateCompanyDto, client_token: str):
    logger.info(f"Попытка изменения данных компании с ID {company_id}")
    logger.info(f"client_token: {client_token}")
    try:
        # Декодирование токена и проверка роли
        await is_user_admin(client_token)

        # Создаем запрос для получения компании по ID
        result = await db.execute(select(CompanyTable).where(CompanyTable.id == company_id))
        db_company = result.scalars().first()  # Получаем первую найденную запись
        if not db_company:
            logger.warning(f"Компания с ID {company_id} не найдена")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Компания не найдена")

        db_company = await get_company(db, company_id)  # Предполагается, что get_company асинхронная

        for var, value in vars(company_data).items():
            if value is not None:  # Обновляем только те поля, которые были указаны
                setattr(db_company, var, value)

        # Коммитим изменения в базе данных
        await db.commit()
        await db.refresh(db_company)

        return db_company
    except HTTPException as e:
        # Если это уже HTTPException, просто пробрасываем его дальше
        raise e
    except Exception as e:
        # Обработка других ошибок
        logging.error(f"Ошибка при обновлении компании: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def update_company_status(db: AsyncSession, company_id: int, is_active: bool, client_token: str):
    logger.info(f"Попытка изменения статуса компании с ID {company_id}")
    logger.info(f"client_token: {client_token}")
    try:
        # Декодирование токена и проверка роли
        await is_user_admin(client_token)

        # Создаем запрос для получения компании по ID
        result = await db.execute(select(CompanyTable).where(CompanyTable.id == company_id))
        db_company = result.scalars().first()  # Получаем первую найденную запись
        if not db_company:
            logger.warning(f"Компания с ID {company_id} не найдена")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Компания не найдена")

        elif db_company:
            # Обновляем статус компании
            db_company.is_active = is_active

            # Выполняем коммит изменений
            await db.commit()

            # Обновляем объект после коммита
            await db.refresh(db_company)
            return db_company

    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса компании: {str(e)}")
        raise


async def delete_company(db: AsyncSession, company_id: int, client_token: str) -> Dict:
    """
    Функция для удаления компании.

    Args:
        db (AsyncSession): Сессия базы данных.
        company_id (int): ID удаляемой компании.
        client_token (str): Токен доступа клиента.

    Returns:
        Dict: Словарь с информацией об удаленной компании.

    Raises:
        HTTPException: В случае ошибки, выбрасывается HTTP-исключение с соответствующим кодом состояния и описанием.
    """

    logger.info(f"Попытка удаления компании с ID {company_id}")
    logger.info(f"client_token: {client_token}")

    try:
        # Декодирование токена и проверка роли
        await is_user_admin(client_token)

        # Создаем запрос для получения компании по ID
        result = await db.execute(select(CompanyTable).where(CompanyTable.id == company_id))
        db_company = result.scalars().first()  # Получаем первую найденную запись

        if not db_company:
            logger.warning(f"Компания с ID {company_id} не найдена")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Компания не найдена")

        await db.delete(db_company)  # Асинхронное удаление
        await db.commit()  # Асинхронный коммит

        logger.info(f"Компания с ID {company_id} успешно удалена")
        return {"detail": "Компания успешно удалена", "company_id": company_id}

    except HTTPException as e:
        # Если произошла HTTPException, просто пробрасываем её дальше
        logger.warning(str(e.detail))
        raise e

    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

#
#
# def delete_all(db: Session):
#     db.query(models.Company).delete()
#     db.query(models.Employee).delete()
#     db.query(models.Service).delete()
#     db.query(models.User).delete()
#     db.commit()
