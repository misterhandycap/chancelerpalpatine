from typing import List

from sqlalchemy import BigInteger, Column, select, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, subqueryload

from bot.models import engine, Base
from bot.models.server_config_autoreply import ServerConfigAutoreply


class ServerConfig(Base):
    __tablename__ = 'server_config'
    id = Column(BigInteger, primary_key=True, nullable=False)
    language = Column(String, default='en')
    autoreply_configs = relationship(ServerConfigAutoreply, lazy='subquery')

    @classmethod
    async def all(cls) -> List['ServerConfig']:
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(ServerConfig).options(subqueryload(ServerConfig.autoreply_configs))
            )).scalars().fetchall()
    
    @classmethod
    async def get(cls, server_id: int) -> 'ServerConfig':
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(ServerConfig).where(ServerConfig.id == server_id)
            )).scalars().first()
    
    @classmethod
    async def save(cls, server_config: 'ServerConfig') -> int:
        async with AsyncSession(engine) as session:
            session.add(server_config)
            await session.commit()
            return server_config.id
