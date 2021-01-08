from uuid import uuid4

from sqlalchemy import BigInteger, Column, ForeignKey, SmallInteger, String
from sqlalchemy.orm import relationship

from bot.models import Base
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
