import os
import sys

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POOL_SIZE = 100

load_dotenv()
db_url = os.environ.get("DB_TESTING_URL") if 'unittest' in sys.modules else os.environ.get("DB_URL")
engine = create_async_engine(db_url, pool_size=POOL_SIZE)
Session = sessionmaker(bind=engine)

Base = declarative_base()
