from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.auth.crud import router as AuthRouter
from app.company.crud import create_company_table_sync, create_test_companies
from app.company.items import router as CompanyRouter
from app.database import get_db, engine
from app.employee.crud import create_employee_table_sync, create_test_employees
from app.employee.items import router as EmployeeRouter
from app.superadmin.items import router as SuperAdminRouter
from app.users.crud import create_test_users, create_users_table_sync
from app.utils.radis import init_redis, close_redis


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Действия при запуске приложения
    # async with engine.begin() as conn:
    #     # Cоздание таблиц
    #     await conn.run_sync(create_users_table_sync)
    #     await conn.run_sync(create_company_table_sync)
    #     await conn.run_sync(create_employee_table_sync)
    #     # Настройка Redis
    # await init_redis()
    try:
        # Создание тестовых пользователей, компаний и сотрудников
        async for db in get_db():
            await create_test_users(db)
            await create_test_companies(db)
            await create_test_employees(db)
        yield
    finally:
        # Закрываем соединение с Redis
        await close_redis()


app = FastAPI(title="X-Clients",
              description=(
                  "<style>"
                  "  .description-text { line-height: 2; }"  # Увеличиваем межстрочный интервал
                  "</style>"
                  "Сервис для отработки навыков работы с БД. "
                  "<br><br>"  # Два разрыва строки для большего разделения
                  "<span class='description-text'>"
                  "<a href='https://www.tinkoff.ru/rm/r_OXMifAgLTf.heDNOPHpld/U6Ubh43680' target='_blank'>Поддержать разработчика</a>"
                  "</span>"
              ),
              version="1.0.0",
              summary="Сервис обращается к БД, расположенной на удаленном сервере",
              openapi_url="/openapi.json",
              contact={"Author": "Евгений Воронов",
                       "Message": "Я тоже учился в SkyPro, и я тоже очень люблю тестить. "
                                  "Успехов Вам  - верю что у вас все получится!."},
              lifespan=lifespan  # Подключение lifespan менеджера

              )

# Подключение роутера
app.include_router(AuthRouter)
app.include_router(CompanyRouter)
app.include_router(EmployeeRouter)
app.include_router(SuperAdminRouter)

# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True)
