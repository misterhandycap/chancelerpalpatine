from datetime import datetime
from uuid import uuid4

from factory import Sequence, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from bot.models.astrology_chart import AstrologyChart
from tests.factories.user_factory import UserFactory
from tests.support.db_connection import Session


class AstrologyChartFactory(SQLAlchemyModelFactory):
    class Meta:
        model = AstrologyChart
        sqlalchemy_session = Session

    id = Sequence(lambda _: uuid4())
    user = SubFactory(UserFactory)
    datetime = datetime.utcnow()
    timezone = '+03:00:00'
    latitude = 10.5
    longitude = 12.5
