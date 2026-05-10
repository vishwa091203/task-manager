from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import StatusEnum

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    project_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    assignee_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
