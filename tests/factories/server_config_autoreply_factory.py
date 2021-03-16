from uuid import uuid4

from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from bot.models.server_config_autoreply import ServerConfigAutoreply
from tests.support.db_connection import Session


class ServerConfigAutoreplyFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ServerConfigAutoreply
        sqlalchemy_session = Session

    id = Sequence(lambda _: uuid4())
    server_config_id = Sequence(lambda n: n)
    message_regex = Sequence(lambda n: f'pattern{n}')
