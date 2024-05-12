from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TaskBase(BaseModel):
    title: str

class TaskCreate(TaskBase):
    pass 

class Task(TaskBase):
    id: int
    completed: bool

    class Config:
        orm_mode = True