from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

db = "mysql+pymysql://root:root@localhost/TODOAPP"

engine = create_engine(db)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush= False,
    bind=engine
)

Base = declarative_base()
