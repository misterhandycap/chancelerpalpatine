from sqlalchemy import BigInteger, Column, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import engine, Base


class ServerConfig(Base):
    __tablename__ = 'server_config'
    id = Column(BigInteger, primary_key=True, nullable=False)
    language = Column(String, default='en')

    @classmethod
    async def all(cls):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(ServerConfig)
            )).scalars().fetchall()
    
    @classmethod
    async def get(cls, server_id):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(ServerConfig).where(ServerConfig.id == server_id)
            )).scalars().first()
    
    @classmethod
    async def save(cls, server_config):
        async with AsyncSession(engine) as session:
            session.add(server_config)
            await session.commit()
            return server_config.id
