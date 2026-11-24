from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.workers.jobs import notify_todo_created
from app.workers.celery_app import celery_app
from . import service
from .schemas import TodoCreate, TodoUpdate, TodoOut

router = APIRouter(prefix="/todos", tags=["Todos & Background jobs"])

@router.post("", status_code=201)
def create(body: TodoCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    todo = service.create(db, body, user)
    # Scheduling failure must be visible; DB record is already committed.
    try:
        job = notify_todo_created.delay(todo.id, todo.title, user.email)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Task saved but notification queue unavailable: {exc.__class__.__name__}") from exc
    return {"todo": TodoOut.model_validate(todo).model_dump(), "notification_task_id": job.id}

@router.get("", response_model=list[TodoOut])
def list_items(project_id: int, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_todos(db, project_id, user, skip, limit)

@router.get("/job/{task_id}")
def job_status(task_id: str, user: User = Depends(get_current_user)):
    result = celery_app.AsyncResult(task_id)
    data = {"task_id": task_id, "status": result.status, "result": None}
    if result.successful():
        # Notification contains no secret, but only authenticated clients may read.
        if result.result.get("recipient") != user.email and user.role != "admin":
            raise HTTPException(status_code=403, detail="Not your notification")
        data["result"] = result.result
    elif result.failed():
        data["result"] = "Background task failed"
    return data

@router.get("/{todo_id}", response_model=TodoOut)
def get(todo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.owned_todo(db, todo_id, user)

@router.patch("/{todo_id}", response_model=TodoOut)
def update(todo_id: int, body: TodoUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.update(db, service.owned_todo(db, todo_id, user), body)

@router.delete("/{todo_id}", status_code=204)
def delete(todo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.delete(db, service.owned_todo(db, todo_id, user))
    return Response(status_code=204)
