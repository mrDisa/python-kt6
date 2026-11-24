from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Todo, User
from app.modules.projects.service import owned_project
from .schemas import TodoCreate, TodoUpdate

def owned_todo(db: Session, todo_id: int, user: User) -> Todo:
    obj = db.get(Todo, todo_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    owned_project(db, obj.project_id, user)
    return obj

def create(db: Session, body: TodoCreate, user: User) -> Todo:
    owned_project(db, body.project_id, user)
    obj = Todo(**body.model_dump(), creator_id=user.id)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def list_todos(db: Session, project_id: int, user: User, skip: int, limit: int):
    owned_project(db, project_id, user)
    return db.scalars(select(Todo).where(Todo.project_id == project_id).order_by(Todo.id).offset(skip).limit(limit)).all()

def update(db: Session, obj: Todo, body: TodoUpdate) -> Todo:
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(obj, key, val)
    db.commit(); db.refresh(obj)
    return obj

def delete(db: Session, obj: Todo):
    db.delete(obj); db.commit()
