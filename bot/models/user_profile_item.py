from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Base, engine
from bot.models.guid import GUID


class UserProfileItem(Base):
    __tablename__ = 'user_profile_item'
    user_id = Column(BigInteger, ForeignKey('user.id'), primary_key=True)
    profile_item_id = Column(GUID, ForeignKey('profile_item.id'), primary_key=True)
    profile_item = relationship('ProfileItem')
    equipped = Column(Boolean, nullable=False, default=False)

    @classmethod
    async def save(cls, user_profile_item):
        async with AsyncSession(engine) as session:
            session.add(user_profile_item)
            await session.commit()
            return user_profile_item.user_id, user_profile_item.profile_item_id
