from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import engine, Base, get_db
from routers import projects, tasks, dashboard
import auth, models, schemas
from sqlalchemy.orm import Session
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/projects-page", response_class=HTMLResponse)
def projects_page(request: Request):
    return templates.TemplateResponse(request, "project.html")

@app.get("/tasks-page", response_class=HTMLResponse)
def tasks_page(request: Request):
    return templates.TemplateResponse(request, "tasks.html")

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(user.password)
    role = models.RoleEnum.admin if not db.query(models.User).filter_by(role=models.RoleEnum.admin).first() else models.RoleEnum.member
    db_user = models.User(name=user.name, email=user.email, password_hash=hashed, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = auth.create_token({"sub": str(db_user.id)})
    return {"token": token, "user": {"id": db_user.id, "name": db_user.name, "role": db_user.role}}

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter_by(email=user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_token({"sub": str(db_user.id)})
    return {"token": token, "user": {"id": db_user.id, "name": db_user.name, "role": db_user.role}}
