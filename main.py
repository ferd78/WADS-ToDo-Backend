from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Task as DBTask
from schemas import TaskCreate, Task

app = FastAPI()

# declare origin/s
origins = [
    "http://localhost:5173",
    "localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating database tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
create_tables()

@app.post("/createTask", response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = DBTask(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/getTaskById/{task_id}", response_model=Task)
def get_task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if task:
        return task
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.get("/getTaskByTitle/{title}", response_model=list[Task])
def get_task_by_title(title: str, db: Session = Depends(get_db)):
    tasks = db.query(DBTask).filter(DBTask.title == title).all()
    if tasks:
        return tasks
    else:
        raise HTTPException(status_code=404, detail=f"No tasks found with title '{title}'")

@app.delete("/deleteById/{task_id}", response_model=dict)
def delete_task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return {"message": "Task deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/deleteByTitle/{title}", response_model=dict)
def delete_task_by_title(title: str, db: Session = Depends(get_db)):
    tasks = db.query(DBTask).filter(DBTask.title == title).all()
    if tasks:
        for task in tasks:
            db.delete(task)
        db.commit()
        return {"message": f"All tasks with title '{title}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"No tasks found with title '{title}'")

@app.delete("/deleteAll", response_model=dict)
def delete_all_tasks(db: Session = Depends(get_db)):
    db.query(DBTask).delete()
    db.commit()
    return {"message": "All tasks deleted successfully"}

@app.get("/getAllTasks", response_model=list[Task])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(DBTask).all()

@app.put("/updateTask/{task_id}", response_model=dict)
def update_task(task_id: int, updated_task: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if task:
        for var, value in vars(updated_task).items():
            setattr(task, var, value)
        db.commit()
        return {"message": "Task updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, debug=True)
