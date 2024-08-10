from database import SessionLocal
from sqlalchemy import select, not_, and_
from models.user import User


async def add_user(user_id, chat_id):
    user = User(
        user_id=str(user_id),
        chat_id=str(chat_id)
    )
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(User).where(str(User.user_id) == str(user_id))
            result = await session.execute(stmt)
            result = result.scalar_one_or_none()
            if not result:
                session.add(user)
                await session.commit()


async def get_users():
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(User)
            result = await session.execute(stmt)
            return list(map(lambda x: x[0].chat_id, result.all()))
