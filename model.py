from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Todo(Base):
    __tablename__ = "TODOS"

    tid = Column("TID", Integer, primary_key=True, index=True)
    title = Column("TITLE", String)
    completed = Column("COMPLETED", Boolean, default=False)