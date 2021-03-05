from random import randint, choice
from uuid import uuid4

from factory import Faker, Sequence
from factory.alchemy import SQLAlchemyModelFactory

from bot.models.planets import Planet
from tests.support.db_connection import Session


class PlanetFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Planet
        sqlalchemy_session = Session

    id = Sequence(lambda _: uuid4())
    name = Faker('name')
    happines_base = randint(0, 100)
    importance_base = randint(0, 100)
    price = randint(10000, 100000)
    region = choice(['Orla Exterior', 'Orla Média', 'Núcleo'])
    climate = Faker('name')
    circuference = randint(100, 10000)
