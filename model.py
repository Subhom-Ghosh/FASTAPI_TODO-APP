from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    tid = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100))
    username = Column(String(100), unique=True)
    password = Column(String(200))
    role = Column(String(20), default="user")

    todos = relationship("Todo", back_populates="owner")