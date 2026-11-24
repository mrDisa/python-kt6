from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.models import User
from app.db.session import get_db
from . import service
from .schemas import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectOut, status_code=201)
def create(body: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.create(db, body, user)

@router.get("", response_model=list[ProjectOut])
def list_projects(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_owned(db, user, skip, limit)

@router.get("/{project_id}", response_model=ProjectOut)
def get(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.owned_project(db, project_id, user)

@router.patch("/{project_id}", response_model=ProjectOut)
def update(project_id: int, body: ProjectUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.update(db, service.owned_project(db, project_id, user), body)

@router.delete("/{project_id}", status_code=204)
def delete(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.delete(db, service.owned_project(db, project_id, user))
    return Response(status_code=204)
