from sqlalchemy import BigInteger, Column, DateTime, Integer, select, String
from sqlalchemy.orm import relationship, subqueryload
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import engine, Base
from bot.models.user_profile_item import user_profile_item_table



class User(Base):
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String, nullable=True)
    currency = Column(Integer, default=0)
    daily_last_collected_at = Column(DateTime, nullable=True)
    profile_items = relationship("ProfileItem", secondary=user_profile_item_table)

    @classmethod
    async def get(cls, user_id, preload_profile_items=False):
        query = select(User).where(User.id == user_id)
        if preload_profile_items:
            query = query.options(
                subqueryload(User.profile_items)
            )
        async with AsyncSession(engine) as session:
            return (await session.execute(query)).scalars().first()
    
    @classmethod
    async def save(cls, user):
        async with AsyncSession(engine) as session:
            session.add(user)
            await session.commit()
            return user.id
