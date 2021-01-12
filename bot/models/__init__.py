import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POOL_SIZE = 100

load_dotenv()
engine = create_engine(os.environ.get("DB_URL"), pool_size=POOL_SIZE)
Session = sessionmaker(bind=engine)

Base = declarative_base()
