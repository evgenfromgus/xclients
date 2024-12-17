import logging
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .schemas import UpdateCompanyStatusDto
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/company", tags=["company"])


@router.get(
    "/list",
    summary="Получение списка компаний",
    description="Запрос выводит все компании в зависимости от статуса активности",
    response_model=list[schemas.CompanyCreateResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Успешно))"},
        401: {"description": "Неверные данные запроса"},
    },
)
async def read_companies(
    db: AsyncSession = Depends(get_db), active: Optional[bool] = None
):
    """
    Обработчик GET-запроса для получения списка компаний.

    Args:
        db (AsyncSession): Сессия базы данных.
        active (Optional[bool]): Фильтр по статусу активности компании (True - активные, False - неактивные).

    Returns:
        List[schemas.Company]: Список компаний, соответствующих фильтру.

    Raises:
        HTTPException: В случае ошибки, выбрасывается HTTP-исключение с соответствующим кодом состояния.
    """
    companies = await crud.get_companies(db, active_only=active)
    return companies


@router.get(
    "/{company_id}",
    summary="Получение данных компании по ID",
    description="Запрос выводит информацию о конкретной компании",
    response_model=schemas.CompanyCreateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Запрос успешно прошел"},
        404: {"description": "Компания не найдена"},
    },
)
async def read_company(company_id: int, db: AsyncSession = Depends(get_db)):
    """
    Обработчик GET-запроса для получения информации о компании по ID.

    Args:
        company_id (int): ID компании, информацию о которой необходимо получить.
        db (AsyncSession): Сессия базы данных.

    Returns:
        schemas.Company: Информация о компании.

    Raises:
        HTTPException: В случае, если компания с указанным ID не найдена, выбрасывается исключение с кодом 404.
    """
    company = await crud.get_company(db, company_id=company_id)
    return company


@router.delete(
    "/{company_id}",
    summary="Удаление компании по ID",
    description="Запрос удаляет конкретную компанию. "
    "Доступно только для пользователей с ролью admin",
    response_model=schemas.DeleteCompanyDto,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Компания успешно удалена"},
        404: {"description": "Компания не найдена"},
        400: {"description": "Неверный формат ID компании"},
        401: {"description": "Неверный токен"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def delete_company(
    company_id: int, client_token: str, db: AsyncSession = Depends(get_db)
):
    """
    Обработчик DELETE-запроса для удаления компании.

    Args:
        company_id (int): ID удаляемой компании.
        client_token (str): Токен доступа клиента.
        db (AsyncSession): Сессия базы данных.

    Returns:
        Dict: Словарь с информацией об удаленной компании или сообщением об ошибке.

    Raises:
        HTTPException: В случае ошибки, выбрасывается HTTP-исключение с соответствующим кодом состояния.
    """

    return await crud.delete_company(db, company_id, client_token)


@router.post(
    "/create",
    summary="Создание новой компании",
    description="Запрос создает новую компанию по заданным параметрам",
    response_model=schemas.CompanyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Компания успешно создана"},
        400: {"description": "Ошибка при создании компании"},
    },
)
async def create_new_company(
    company_data: schemas.CompanyCreateRequest, db: AsyncSession = Depends(get_db)
):
    """
    Обработчик POST-запроса для создания новой компании.

    Args:
        company_data (schemas.Company): Данные новой компании.
        db (AsyncSession): Сессия базы данных.

    Returns:
        schemas.CreateCompanyDto: Информация о созданной компании.

    Raises:
        HTTPException: В случае ошибки валидации или создания компании, выбрасывается исключение с соответствующим кодом состояния.
    """
    return await crud.create_company(db=db, company_data=company_data)


@router.patch(
    "/update/{company_id}",
    summary="Обновление данных компании",
    description="Запрос изменяет имя и описание компании. "
    "Доступно только для пользователей с ролью admin",
    response_model=schemas.UpdateCompanyDto,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Компания успешно обновлена"},
        404: {"description": "Компания не найдена"},
        400: {"description": "Ошибка при обновлении компании"},
        403: {"description": "Доступ запрещен"},
    },
)
async def patch_company(
    company_id: int,
    updated_company: schemas.UpdateCompanyDto,
    client_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Обработчик PATCH-запроса для обновления данных компании.

    Args:
        company_id (int): ID компании, данные которой необходимо обновить.
        updated_company (schemas.UpdateCompanyDto): Новые данные компании.
        client_token (str): Токен доступа клиента для проверки роли администратора.
        db (AsyncSession): Сессия базы данных.

    Returns:
        schemas.UpdateCompanyDto: Обновленные данные компании.

    Raises:
        HTTPException: В случае, если компания не найдена, токен невалиден или пользователь не является администратором, выбрасывается исключение с соответствующим кодом состояния.
    """
    return await crud.update_company_data(
        db,
        company_id=company_id,
        company_data=updated_company,
        client_token=client_token,
    )


@router.patch(
    "/status_update/{company_id}",
    summary="Обновление статуса компании",
    description="Запрос обновляет статус компании в зависимости от заданного значения."
    "Доступно только для пользователей с ролью admin",
    response_model=schemas.UpdateCompanyStatusDto,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Статус компании успешно обновлен"},
        401: {"description": "Неверный токен"},
        404: {"description": "Компания не найдена"},
    },
)
async def update_status(
    company_id: int,
    company_status: UpdateCompanyStatusDto,
    client_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Обработчик PATCH-запроса для обновления статуса компании.

    Args:
        company_id (int): ID компании, статус которой необходимо обновить.
        company_status (UpdateCompanyStatusDto): Новый статус компании.
        client_token (str): Токен доступа клиента для проверки роли администратора.
        db (AsyncSession): Сессия базы данных.

    Returns:
        schemas.UpdateCompanyStatusDto: Обновленный статус компании.

    Raises:
        HTTPException: В случае, если компания не найдена, токен невалиден или пользователь не является администратором, выбрасывается исключение с соответствующим кодом состояния.
    """
    logger.info(f"Обновление статуса компании {company_id} с токеном {client_token}")

    db_company = await crud.update_company_status(
        db,
        company_id=company_id,
        is_active=company_status.is_active,
        client_token=client_token,
    )

    logger.info(
        f"Статус компании {company_id} успешно обновлен на {db_company.is_active}"
    )
    return UpdateCompanyStatusDto(is_active=db_company.is_active)
