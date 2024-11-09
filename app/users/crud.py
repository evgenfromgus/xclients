from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine
from app.users.schemas import UserTable, User, Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_users_table():
    async with engine.begin() as conn:
        await conn.run_sync(create_users_table_sync)


def create_users_table_sync(conn):
    Base.metadata.tables['app_users'].create(conn, checkfirst=True)


async def create_test_users(db: AsyncSession):
    # Очистка таблицы пользователей
    await db.execute(text("TRUNCATE TABLE app_users RESTART IDENTITY"))
    # await db.execute(delete(UserTable))
    await db.commit()

    # Список тестовых пользователей
    users = [
        User(username='harrypotter', password='expelliarmus', role='admin'),
        User(username='hermione', password='leviosa', role='client'),
        User(username='ronweasley', password='chessmaster', role='client'),
        User(username='dumbledore', password='phoenix', role='client'),
        User(username='snape', password='potionmaster', role='admin'),
        User(username='lunalovegood', password='nargles', role='client'),
        User(username='neville', password='herbology', role='client'),
        User(username='ginny', password='batbogey', role='admin'),
        User(username='hagrid', password='fluffy', role='client'),
        User(username='draco', password='malfoy', role='client'),
        User(username='mcgonagall', password='animagus', role='client'),
        # Суперпользователь - пароль никому не говорить!!!
        User(username='voldemort', password='ExpectoPatronum123!', role='admin')
    ]

    for user in users:
        # Хеширование пароля - чтобы не было видно все пароли в общей таблице
        hashed_password = pwd_context.hash(user.password)
        db_user = UserTable(
            login=user.username,
            password=hashed_password,
            display_name=user.username,
            role=user.role
        )
        db.add(db_user)

    await db.commit()
