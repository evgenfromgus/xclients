from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from . import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/employee", tags=["employee"])


@router.get("/info/{employee_id}",
            summary="Получение данных о сотруднике по ID",
            description="Запрос предоставляет данные о сотруднике по его ID",
            status_code=status.HTTP_200_OK,
            response_model=schemas.Employee,
            responses={
                200: {"description": "Сотрудник найден"},
                404: {"description": "Сотрудник не найден"},
                422: {"description": "Ошибка валидации"}
            })
async def read_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    employee = await crud.get_employee(db, employee_id=employee_id)
    return employee


@router.post("/create",
             summary="Создание сотрудника",
             description="Запрос создает сотрудника с заданными параметрами",
             status_code=status.HTTP_200_OK,
             response_model=schemas.Employee,
             responses={
                 200: {"description": "Сотрудник создан"},
                 404: {"description": "Сотрудник не создан или создан с ошибкой"},
                 422: {"description": "Ошибка валидации"}
             })
async def create_employee(employee: schemas.Employee, db: AsyncSession = Depends(get_db)):
    new_employee = await crud.create_employee(db=db, employee=employee)
    return new_employee


@router.get("/list/{company_id}",
            summary="Получение списка сотрудников компании по ее ID",
            description="Запрос предоставляет список сотрудников по ID компании",
            status_code=status.HTTP_200_OK,
            response_model=List[schemas.Employee],
            responses={
                200: {"description": "Сотрудники найдены"},
                404: {"description": "Сотрудники не найдены"},
                422: {"description": "Ошибка валидации"}
            })
async def get_list_employee(company_id: int, db: AsyncSession = Depends(get_db)):
    employees = await crud.get_employees(db, company_id=company_id)
    return employees


@router.patch("/change/{employee_id}",
              summary="Изменение информации о сотруднике",
              description="Запрос изменяет данные сотрудника",
              status_code=status.HTTP_200_OK,
              response_model=schemas.Employee,
              responses={
                  200: {"description": "Информация изменена"},
                  404: {"description": "Сотрудник не найден"},
                  422: {"description": "Ошибка валидации"}
              })
async def update_employee(employee_id: int,
                          client_token: str,
                          updated_employee: schemas.UpdateEmployeeDto,
                          db: AsyncSession = Depends(get_db)
                          ):
    return await crud.update_employee(db, employee_id=employee_id,
                                      update_data=updated_employee,
                                      client_token=client_token)
