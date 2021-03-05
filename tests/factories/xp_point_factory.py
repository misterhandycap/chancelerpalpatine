from datetime import datetime

from factory import Sequence, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from bot.models.xp_point import XpPoint
from tests.factories.user_factory import UserFactory
from tests.support.db_connection import Session


class XpPointFactory(SQLAlchemyModelFactory):
    class Meta:
        model = XpPoint
        sqlalchemy_session = Session

    user = SubFactory(UserFactory)
    server_id = Sequence(lambda n: n)
    updated_at = datetime.utcnow()
    points = 0
    level = 1
