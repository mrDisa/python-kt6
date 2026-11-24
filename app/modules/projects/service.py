from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Project, User
from .schemas import ProjectCreate, ProjectUpdate

def owned_project(db: Session, project_id: int, user: User) -> Project:
    obj = db.get(Project, project_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if obj.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your project")
    return obj

def create(db: Session, data: ProjectCreate, user: User) -> Project:
    obj = Project(**data.model_dump(), owner_id=user.id)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def list_owned(db: Session, user: User, skip: int, limit: int):
    query = select(Project).order_by(Project.id).offset(skip).limit(limit)
    if user.role != "admin":
        query = query.where(Project.owner_id == user.id)
    return db.scalars(query).all()

def update(db: Session, obj: Project, data: ProjectUpdate) -> Project:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit(); db.refresh(obj)
    return obj

def delete(db: Session, obj: Project):
    db.delete(obj); db.commit()
