from fastapi import FastAPI,Depends
from sqlalchemy import text
from database import engine
from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import SessionLocal,engine
from sqlalchemy import text
import model
import schemas

app = FastAPI()

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
    

@app.get("/TODOS")
def get_todos(db: Session=Depends(get_db)):
    todos = db.query(model.Todo).all()

    return{
        "message":"Todos fetched Successfully",
        "todos":todos
    }  
#post route
@app.post("/TODOS")
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    new_todo = model.Todo(
        title=todo.title
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return {
        "message": "Todo added successfully 🎉",
        "todo": new_todo
    }

#---------------Delete-----------------
@app.delete(("/TODOS/{todo_id}"))
def delete_todo(todo_id:int, db: Session=Depends(get_db)):
    todo = db.query(model.Todo).filter(model.Todo.tid==todo_id).first()

    if not todo:
        return {"message":"Enter valid tid"}
    db.delete(todo)
    db.commit()

    return{
        "message" : "TOdo Deleted Successfully"
    }


#------------------UPDATE-------------------

@app.put("/TODOS/{todo_id}")
def update_todo(todo_id: int, updated_todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    todo = db.query(model.Todo).filter(model.Todo.tid == todo_id).first()

    if not todo:
        return {
            "message": "Todo not found"
        }

    todo.title = updated_todo.title
    todo.completed = updated_todo.completed

    db.commit()
    db.refresh(todo)

    return {
        "message": "Todo updated successfully ✨",
        "todo": todo
    }