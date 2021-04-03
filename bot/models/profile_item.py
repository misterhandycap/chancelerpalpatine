import enum
import logging
from io import BytesIO
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, func, Integer, select, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import validates

from bot.models import Base, engine
from bot.models.exceptions import ProfileItemException
from bot.models.guid import GUID


class ProfileItemType(enum.Enum):
    badge = 1
    wallpaper = 2


class ProfileItem(Base):
    __tablename__ = 'profile_item'
    id = Column(GUID(), primary_key=True, default=uuid4)
    type = Column(Enum(ProfileItemType), nullable=False)
    name = Column(String, nullable=False, unique=True)
    price = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)

    @validates('type')
    def validate_type(self, key, value):
        if value not in ProfileItemType.__members__.keys():
            raise ProfileItemException('Invalid profile item type')
        return value

    @validates('price')
    def validate_price(self, key, value):
        if not(isinstance(value, int) and value > 0):
            raise ProfileItemException('Profile item price must be greater than zero')
        return value

    @classmethod
    async def get(cls, item_id):
        try:
            async with AsyncSession(engine) as session:
                return (await session.execute(
                    select(ProfileItem).where(ProfileItem.id == item_id))).scalars().first()
        except:
            return None

    @classmethod
    async def get_by_name(cls, item_name):
        async with AsyncSession(engine) as session:
            return (await session.execute(
                select(ProfileItem).where(ProfileItem.name == item_name))).scalars().first()

    @classmethod
    async def all(cls, search=None, page=0, page_size=9):
        async with AsyncSession(engine) as session:
            query = select(ProfileItem).offset(page*page_size).limit(page_size)
            total_query = select(func.count(ProfileItem.id))
            if search:
                query = query.filter(ProfileItem.name.contains(search))
                total_query = total_query.filter(ProfileItem.name.contains(search))
                
            page_content = (await session.execute(query)).scalars().fetchall()
            total_entries = (await session.execute(total_query)).scalar()
            last_page = int(total_entries // page_size) + (total_entries % page_size > 0)
            return page_content, last_page

    @classmethod
    async def save(cls, profile_item):
        async with AsyncSession(engine) as session:
            session.add(profile_item)
            await session.commit()
            return profile_item.id

    def get_file_contents(self):
        try:
            with open(self.file_path, 'rb') as f:
                return BytesIO(f.read())
        except Exception as e:
            logging.warning(e)
            return None
