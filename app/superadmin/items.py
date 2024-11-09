import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from ..company.crud import create_company_table_sync, create_test_companies
from ..database import get_db, engine
from ..employee.crud import create_employee_table_sync, create_test_employees
from ..users.crud import create_users_table_sync, create_test_users

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/magic', tags=["superuser"])


@router.get("/delete_create_all",
            summary="Полный рефреш",
            description="Только темные силы смогут это сделать.\n"
                        "Подумай - нужно ли тебе это?\n"
                        "Мы уничтожим все таблицы, потом пересоздадим их и заполним тестовыми данными.",
            status_code=status.HTTP_200_OK,
            responses={
                200: {"description": "Шалось удалась"},
                403: {"description": "Доступ запрещен"}
            })
async def refresh_db(client_token: str, db: AsyncSession = Depends(get_db)):
    await crud.delete_all_tables(db, client_token=client_token)
    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(create_users_table_sync)
        await conn.run_sync(create_company_table_sync)
        await conn.run_sync(create_employee_table_sync)

    # Создание тестовых данных
    await create_test_companies(db)
    await create_test_users(db)
    await create_test_employees(db)

    await db.commit()
    return {"message": "Все снесено и пересоздано - ты красава, "
                       "но не увлекайся этой темной магией."}

