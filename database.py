import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Use environment variable for DB URL, fallback to local for development
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost/TODOAPP")

# Fix: Only use SSL arguments if we are connecting to the live Aiven cloud database
if "aivencloud" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"ssl": {}})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()