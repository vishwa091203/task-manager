from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/tasks", tags=["tasks"])
security = HTTPBearer()

def serialize_task(task: models.Task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "due_date": task.due_date,
        "project_id": task.project_id,
        "assignee_id": task.assignee_id,
        "created_at": task.created_at,
    }

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/")
def get_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "admin":
        tasks = db.query(models.Task).all()
        return [serialize_task(task) for task in tasks]
    tasks = db.query(models.Task).filter(models.Task.assignee_id == current_user.id).all()
    return [serialize_task(task) for task in tasks]

@router.post("/")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create tasks")
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if task.assignee_id is not None:
        assignee = db.query(models.User).filter(models.User.id == task.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
    db_task = models.Task(
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        due_date=task.due_date
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return serialize_task(db_task)

@router.patch("/{task_id}")
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status:
        db_task.status = task.status
    if task.assignee_id is not None:
        db_task.assignee_id = task.assignee_id
    if task.title:
        db_task.title = task.title
    if task.description:
        db_task.description = task.description
    db.commit()
    db.refresh(db_task)
    return serialize_task(db_task)

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete tasks")
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}
