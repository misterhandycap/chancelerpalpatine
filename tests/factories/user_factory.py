from datetime import datetime

from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from bot.models.user import User
from tests.factories.profile_item_factory import ProfileItemFactory
from tests.support.db_connection import Session


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session

    id = Sequence(lambda n: n)
    name = Sequence(lambda n: f'User {n}')
    currency = 100
    daily_last_collected_at = datetime.utcnow()
