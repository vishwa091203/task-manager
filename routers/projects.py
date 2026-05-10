from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/projects", tags=["projects"])
security = HTTPBearer()

def serialize_project(project: models.Project):
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "owner_id": project.owner_id,
        "created_at": project.created_at,
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
def get_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "admin":
        projects = db.query(models.Project).all()
        return [serialize_project(project) for project in projects]
    memberships = db.query(models.ProjectMember).filter_by(user_id=current_user.id).all()
    project_ids = [m.project_id for m in memberships]
    projects = db.query(models.Project).filter(models.Project.id.in_(project_ids)).all()
    return [serialize_project(project) for project in projects]

@router.post("/")
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create projects")
    db_project = models.Project(name=project.name, description=project.description, owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    db.add(models.ProjectMember(project_id=db_project.id, user_id=current_user.id, role="admin"))
    db.commit()
    return serialize_project(db_project)

@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return serialize_project(project)

@router.post("/{project_id}/members")
def add_member(project_id: int, user_id: int, role: str = "member", db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add members")
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if role not in {r.value for r in models.RoleEnum}:
        raise HTTPException(status_code=400, detail="Invalid role")
    existing = db.query(models.ProjectMember).filter_by(project_id=project_id, user_id=user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already a member")
    member = models.ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    return {"message": "Member added"}

@router.get("/{project_id}/members")
def get_members(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    members = db.query(models.ProjectMember).filter_by(project_id=project_id).all()
    result = []
    for m in members:
        user = db.query(models.User).filter(models.User.id == m.user_id).first()
        if not user:
            continue
        result.append({"user_id": m.user_id, "name": user.name, "email": user.email, "role": m.role})
    return result
