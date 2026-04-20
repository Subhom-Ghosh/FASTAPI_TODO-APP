from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str


class TodoUpdate(BaseModel):
    title: str
    completed: bool


class UserCreate(BaseModel):
    fullname: str
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str

from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str