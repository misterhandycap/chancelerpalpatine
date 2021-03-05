import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from bot.models import Base
from bot.models.profile_item import ProfileItem

engine = create_engine(os.environ.get("DB_TESTING_URL"))
Session = scoped_session(sessionmaker(bind=engine))

def clear_data(session):
    meta = Base.metadata

    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()
