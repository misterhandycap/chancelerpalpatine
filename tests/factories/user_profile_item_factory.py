from factory.alchemy import SQLAlchemyModelFactory

from bot.models.user_profile_item import UserProfileItem
from tests.support.db_connection import Session


class UserProfileItemFactory(SQLAlchemyModelFactory):
    class Meta:
        model = UserProfileItem
        sqlalchemy_session = Session

    equipped = True
