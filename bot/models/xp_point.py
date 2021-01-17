from datetime import datetime

from sqlalchemy import (BigInteger, Column, DateTime, ForeignKey, Integer,
                        func, select)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, relationship

from bot.models import Base, engine


class XpPoint(Base):
    __tablename__ = 'xp_point'
    user_id = Column(BigInteger, ForeignKey('user.id'), primary_key=True)
    user = relationship('User', foreign_keys=[user_id])
    server_id = Column(BigInteger, primary_key=True)
    updated_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    points = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)

    @classmethod
    async def get_by_user_and_server(cls, user_id, server_id):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(XpPoint)
                    .where(XpPoint.user_id == user_id)
                    .where(XpPoint.server_id == server_id)
            )).scalars().first()

    @classmethod
    async def list_by_server(cls, server_id):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(XpPoint)
                    .where(XpPoint.server_id == server_id)
                    .order_by(XpPoint.points.desc())
                    .options(joinedload(XpPoint.user))
            )).scalars().fetchall()

    @classmethod
    async def get_user_aggregated_points(cls, user_id):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(func.sum(XpPoint.points)).select_from(XpPoint)
                    .where(XpPoint.user_id == user_id)
            )).scalars().first()

    @classmethod
    async def save(cls, xp_point):
        async with AsyncSession(engine) as session:
            session.add(xp_point)
            await session.commit()
            return xp_point
