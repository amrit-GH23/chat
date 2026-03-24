from .config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL )
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()