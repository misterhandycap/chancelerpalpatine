from sqlalchemy import BigInteger, Column, ForeignKey, Table

from bot.models import Base
from bot.models.guid import GUID

user_profile_item_table = Table('user_profile_item', Base.metadata,
    Column('user_id', BigInteger, ForeignKey('user.id'), primary_key=True),
    Column('profile_item_id', GUID, ForeignKey('profile_item.id'), primary_key=True)
)
