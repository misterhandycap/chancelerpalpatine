from uuid import uuid4

from factory import Faker, Sequence, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from bot.models.chess_game import ChessGame
from tests.factories.user_factory import UserFactory
from tests.support.db_connection import Session


class ChessGameFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ChessGame
        sqlalchemy_session = Session

    id = Sequence(lambda _: uuid4())
    player1 = SubFactory(UserFactory)
    player2 = SubFactory(UserFactory)
    pgn = Faker('text')
    result = None
    color_schema = None
    cpu_level = None
