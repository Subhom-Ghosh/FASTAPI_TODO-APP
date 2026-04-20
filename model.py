from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Todo(Base):
    __tablename__ = "TODOS"

    tid = Column("TID", Integer, primary_key=True, index=True)
    title = Column("TITLE", String(255))
    completed = Column("COMPLETED", Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(50))
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))