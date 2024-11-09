from sqlalchemy import text, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.crud import is_user_superadmin
from app.company.schemas import CompanyTable
from app.employee.schemas import EmployeeTable
from app.users.schemas import UserTable


async def delete_all_tables(db: AsyncSession, client_token: str):
    await is_user_superadmin(client_token)
    async with db.begin():
        await db.execute(delete(UserTable))
        await db.execute(delete(CompanyTable))
        await db.execute(delete(EmployeeTable))
    await db.commit()
