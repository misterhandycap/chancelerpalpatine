from uuid import uuid4

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String

from bot.models import Base
from bot.models.guid import GUID


class ChessGame(Base):
    __tablename__ = 'chess_game'
    id = Column(GUID(), primary_key=True, default=uuid4)
    player1 = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    player2 = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    pgn = Column(String)
    result = Column(Integer, nullable=True)
