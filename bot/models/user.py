from sqlalchemy import BigInteger, Column, Integer, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import engine, Base


class User(Base):
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String, nullable=True)
    xp_points = Column(Integer, default=0)

    @classmethod
    async def get(cls, user_id):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(User).where(User.id == user_id))).scalars().first()
