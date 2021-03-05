import os
from uuid import uuid4

from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from bot.models.profile_item import ProfileItem
from tests.support.db_connection import Session


class ProfileItemFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ProfileItem
        sqlalchemy_session = Session

    id = Sequence(lambda _: uuid4())
    type = 'badge'
    name = Sequence(lambda n: f"Profile item {n}")
    price = 150
    file_path = os.path.join("some", "path")
