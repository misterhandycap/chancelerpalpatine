from sqlalchemy import BigInteger, Column, DateTime, Integer, select, String
from bot.models import engine, Base
from bot.models.guid import GUID
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

class Merchant(Base):
    __tablename__ = 'merchant'
    id = Column(GUID(), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    merchat_amount_reset = Column(DateTime, nullable=True)

    @classmethod
    async def get_by_name(cls, merchant_name):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(Merchant).where(Merchant.name == merchant_name))).scalars().first()

    @classmethod
    async def save(cls, merchant):
        async with AsyncSession(engine) as session:
            session.add(merchant)
            await session.commit()
            return merchant.id