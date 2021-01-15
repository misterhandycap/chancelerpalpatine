from uuid import uuid4

from sqlalchemy import (BigInteger, Column, ForeignKey, SmallInteger, String,
                        select)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, subqueryload

from bot.models import Base, engine
from bot.models.guid import GUID


class ChessGame(Base):
    __tablename__ = 'chess_game'
    id = Column(GUID(), primary_key=True, default=uuid4)
    player1_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    player2_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    player1 = relationship('User', foreign_keys=[player1_id])
    player2 = relationship('User', foreign_keys=[player2_id])
    pgn = Column(String)
    result = Column(SmallInteger, nullable=True)
    color_schema = Column(String, nullable=True)
    cpu_level = Column(SmallInteger, nullable=True)

    @classmethod
    async def get(cls, chess_game_id):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(ChessGame).where(ChessGame.id == chess_game_id)
            )).scalars().first()

    @classmethod
    async def get_all_ongoing_games(cls):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(ChessGame).where(ChessGame.result == None).options(
                    subqueryload(ChessGame.player1),
                    subqueryload(ChessGame.player2)
                )
            )).scalars().fetchall()
    
    @classmethod
    async def save(cls, chess_game):
        async with AsyncSession(engine) as session:
            session.add(chess_game)
            await session.commit()
            return chess_game.id
