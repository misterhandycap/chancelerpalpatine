from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from bot.models.server_config import ServerConfig
from tests.support.db_connection import Session


class ServerConfigFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ServerConfig
        sqlalchemy_session = Session

    id = Sequence(lambda n: n)
    language = 'en'
