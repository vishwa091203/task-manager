# Task Manager Web Application

A full-stack task management web application built with FastAPI, SQLite, SQLAlchemy, Jinja2, HTML, CSS, and JavaScript.

## Live Application URL

https://task-manager-laae.onrender.com

## GitHub Repository

https://github.com/vishwa091203/task-manager

## Overview

This application helps users manage projects and tasks through a simple role-based workflow. Admin users can create projects and tasks, while members can view and update assigned tasks.

The app includes authentication, dashboard analytics, task status tracking, due dates, project management, and a modern glass-style responsive user interface.

## Features

- User signup and login
- JWT-based authentication
- Role-based access control
- Admin and member user roles
- Project creation and listing
- Task creation and listing
- Task status updates
- Dashboard with task statistics
- Overdue task tracking
- Responsive glassmorphism UI
- SQLite database for local storage

## Tech Stack

- Backend: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Authentication: JWT
- Password Hashing: Passlib PBKDF2 SHA256
- Frontend: HTML, CSS, JavaScript
- Templates: Jinja2
- Server: Uvicorn
- Deployment: Render

## User Roles

Admin users can create projects, view all projects, create tasks, view all tasks, delete tasks, add project members, and update task status.

Member users can view projects they belong to, view assigned tasks, and update task status.

## Pages

Login and Signup page allows users to create an account or log in using email and password.

Dashboard page shows total tasks, to-do tasks, in-progress tasks, completed tasks, overdue tasks, logged-in user, and user role.

Projects page displays the project list and allows admin users to create new projects.

Tasks page displays the task list and allows users to update task status.

## Local Setup

1. Clone the repository:

git clone https://github.com/vishwa091203/task-manager.git

2. Open the project folder:

cd task-manager

3. Install dependencies:

pip install -r requirements.txt

4. Run the application:

uvicorn main:app --reload

5. Open in browser:

http://127.0.0.1:8000/

## Deployment

The app can be deployed on Render as a Python web service.

Build Command:

pip install -r requirements.txt

Start Command:

uvicorn main:app --host 0.0.0.0 --port $PORT

## Project Structure

task-manager/
main.py
database.py
models.py
schemas.py
auth.py
requirements.txt
Procfile
routers/
dashboard.py
projects.py
tasks.py
templates/
base.html
login.html
dashboard.html
project.html
tasks.html
static/
style.css

## Notes

The application currently uses SQLite for simplicity. For production deployment, PostgreSQL or another managed database can be used for persistent cloud storage.

## Author

Vishwa Teja Anandeshi

GitHub: https://github.com/vishwa091203
