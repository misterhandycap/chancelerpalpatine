from sqlalchemy import BigInteger, Column, Integer, DateTime, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import engine, Base



class User(Base):
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String, nullable=True)
    currency = Column(Integer, default=0)
    daily_last_collected_at = Column(DateTime, nullable=True)

    @classmethod
    async def get(cls, user_id):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(User).where(User.id == user_id))).scalars().first()
    
    @classmethod
    async def save(cls, user):
        async with AsyncSession(engine) as session:
            session.add(user)
            await session.commit()
            return user.id
