import os
#from http.client import HTTPException
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from sqlalchemy import text
import model
import schemas
from fastapi.middleware.cors import CORSMiddleware
from utils import hash_password, verify_password
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

# It's recommended to load secrets from environment variables rather than hardcoding.
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model.Base.metadata.create_all(bind=engine)

#DB session
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def test_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"message": "Database connected successfully "}
    except Exception as e:
        return {"error": str(e)}
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token ❌")

    user = db.query(model.User).filter(model.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found ❌")

    return user


#post route
@app.post("/TODOS")
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db),current_user: model.User = Depends(get_current_user)):
    new_todo = model.Todo(
        title=todo.title,
        user_id=current_user.id 
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return {
        "message": "Todo added successfully 🎉",
        "todo": new_todo
    }

@app.get("/TODOS")
def get_todos(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    todos = db.query(model.Todo).filter(
        model.Todo.user_id == current_user.id
    ).all()

    return {
        "message": "Todos fetched Successfully",
        "todos": todos
    }


#---------------Delete-----------------
@app.delete("/TODOS/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    todo = db.query(model.Todo).filter(
        model.Todo.tid == todo_id,
        model.Todo.user_id == current_user.id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found or you don't have permission to delete it")

    db.delete(todo)
    db.commit()

    return {"message": "Todo Deleted Successfully "}


#------------------UPDATE-------------------

@app.put("/TODOS/{todo_id}")
def update_todo(
    todo_id: int,
    updated_todo: schemas.TodoUpdate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    todo = db.query(model.Todo).filter(
        model.Todo.tid == todo_id,
        model.Todo.user_id == current_user.id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found or you don't have permission to update it")

    todo.title = updated_todo.title
    todo.completed = updated_todo.completed

    db.commit()
    db.refresh(todo)

    return {
        "message": "Todo updated successfully ✨",
        "todo": todo
    }

#------------------SIGNUP-----------------
@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # user already exist check
    existing_user = db.query(model.User).filter(model.User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = model.User(
        fullname = user.fullname,
        username=user.username,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully 🎉"}


#-------------LOGIN-----------
@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(model.User).filter(model.User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create JWT token
    payload = {
        "sub": db_user.username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": access_token, "token_type": "bearer",
             "username": db_user.username,
             "role": db_user.role,
    "fullname": db_user.fullname
    }


def require_admin(current_user: model.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required ❌")
    return current_user


@app.get("/admin/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    admin: model.User = Depends(require_admin)
):
    total_users = db.query(model.User).count()
    total_todos = db.query(model.Todo).count()

    completed = db.query(model.Todo).filter(model.Todo.completed == True).count()
    pending = db.query(model.Todo).filter(model.Todo.completed == False).count()

    return {
        "total_users": total_users,
        "total_todos": total_todos,
        "completed": completed,
        "pending": pending
    }


@app.get("/admin/users")
def get_all_users(
    db: Session = Depends(get_db),
    admin: model.User = Depends(require_admin)
):
    users = db.query(model.User).all()
    return users



@app.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: model.User = Depends(require_admin)
):
    user = db.query(model.User).filter(model.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@app.get("/admin/todos")
def get_all_todos(
    db: Session = Depends(get_db),
    admin: model.User = Depends(require_admin)
):
    todos = db.query(model.Todo).all()
    return todos


@app.delete("/admin/todos/{todo_id}")
def delete_any_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    admin: model.User = Depends(require_admin)
):
    todo = db.query(model.Todo).filter(model.Todo.tid == todo_id).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted by admin"}
