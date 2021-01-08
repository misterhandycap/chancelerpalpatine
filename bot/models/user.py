from sqlalchemy import BigInteger, Column, Integer

from bot.models import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True, nullable=False)
    xp_points = Column(Integer, default=0)
