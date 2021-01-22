from uuid import uuid4

from sqlalchemy import BigInteger, String, Column, DateTime, Float, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from bot.models import Base, engine
from bot.models.guid import GUID


class AstrologyChart(Base):
    __tablename__ = 'astrology_chart'
    id = Column(GUID(), primary_key=True, default=uuid4)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=[user_id])
    datetime = Column(DateTime, nullable=False)
    timezone = Column(String(9), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    @classmethod
    async def get_by_user_id(cls, user_id):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(AstrologyChart).where(AstrologyChart.user_id == user_id)
            )).scalars().first()

    @classmethod
    async def save(cls, astrology_chart):
        async with AsyncSession(engine) as session:
            session.add(astrology_chart)
            await session.commit()
            return astrology_chart.id
