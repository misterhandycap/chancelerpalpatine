from sqlalchemy import BigInteger, Column, DateTime, Integer, select, String
from bot.models import engine, Base
from bot.models.guid import GUID
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

class Planet(Base):
    __tablename__ = 'planet'
    id = Column(GUID(), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    happines_base = Column(Integer, nullable=False)
    importance_base = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    region = Column(String, nullable=False)
    climate = Column(String, nullable=False)
    circuference = Column(Integer, nullable=False)

    @classmethod
    async def all(cls, region=None, climate=None, circuference=None, mass=None):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(Planet).filter_by(region=region) #, climate=climate, circuference=circuference, mass=mass) 
            )).scalars().fetchall()
