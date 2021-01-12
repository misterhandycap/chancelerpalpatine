import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from bot.models import Base

engine = create_engine(os.environ.get("DB_TESTING_URL"))
Session = sessionmaker(bind=engine)

def clear_data(session):
    meta = Base.metadata

    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()
