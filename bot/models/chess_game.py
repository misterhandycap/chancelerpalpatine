from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (BigInteger, Column, ForeignKey, SmallInteger, String,
                        and_, func, or_, select)
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
    async def get(cls, chess_game_id: str, preload_players: bool=False) -> Optional['ChessGame']:
        query = select(ChessGame).where(ChessGame.id == chess_game_id)
        if preload_players:
            query = query.options(
                subqueryload(ChessGame.player1),
                subqueryload(ChessGame.player2)
            )
        async with AsyncSession(engine) as session:
            return (await session.execute(query)).scalars().first()

    @classmethod
    async def get_all_ongoing_games(cls) -> List['ChessGame']:
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(ChessGame).where(ChessGame.result == None).options(
                    subqueryload(ChessGame.player1),
                    subqueryload(ChessGame.player2)
                )
            )).scalars().fetchall()

    @classmethod
    async def get_number_of_victories(cls, user_id: int) -> int:
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(func.count()).select_from(ChessGame).where(
                    or_(
                        and_(ChessGame.result == 1, ChessGame.player1_id == user_id),
                        and_(ChessGame.result == -1, ChessGame.player2_id == user_id)
                    )
                )
            )).scalars().first()
    
    @classmethod
    async def save(cls, chess_game: 'ChessGame') -> str:
        async with AsyncSession(engine) as session:
            session.add(chess_game)
            await session.commit()
            return chess_game.id
