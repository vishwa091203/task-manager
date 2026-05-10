from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import datetime

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
security = HTTPBearer()

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
def get_dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "admin":
        tasks = db.query(models.Task).all()
    else:
        tasks = db.query(models.Task).filter(models.Task.assignee_id == current_user.id).all()

    now = datetime.datetime.utcnow()
    total = len(tasks)
    todo = len([t for t in tasks if t.status == "todo"])
    in_progress = len([t for t in tasks if t.status == "in_progress"])
    done = len([t for t in tasks if t.status == "done"])
    overdue = len([t for t in tasks if t.due_date and t.due_date < now and t.status != "done"])

    return {
        "total_tasks": total,
        "todo": todo,
        "in_progress": in_progress,
        "done": done,
        "overdue": overdue,
        "user": current_user.name,
        "role": current_user.role
    }