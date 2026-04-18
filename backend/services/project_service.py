from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

from backend.models.project import Project, Task, TaskStatus
from backend.schemas.project import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate


def _calc_progress(tasks: List[Task]) -> float:
    if not tasks:
        return 0.0
    done = sum(1 for t in tasks if t.status == TaskStatus.done)
    return round((done / len(tasks)) * 100, 1)


def get_projects(db: Session, user_id: int) -> List[Project]:
    projects = db.query(Project).filter(Project.user_id == user_id).all()
    for p in projects:
        p.progress = _calc_progress(p.tasks)
    return projects


def get_project(db: Session, user_id: int, project_id: int) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.progress = _calc_progress(project.tasks)
    return project


def create_project(db: Session, user_id: int, data: ProjectCreate) -> Project:
    project = Project(user_id=user_id, **data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    project.progress = 0.0
    return project


def update_project(db: Session, user_id: int, project_id: int, data: ProjectUpdate) -> Project:
    project = get_project(db, user_id, project_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    project.progress = _calc_progress(project.tasks)
    return project


def delete_project(db: Session, user_id: int, project_id: int) -> bool:
    project = get_project(db, user_id, project_id)
    db.delete(project)
    db.commit()
    return True


# --- Tasks ---

def create_task(db: Session, user_id: int, project_id: int, data: TaskCreate) -> Task:
    get_project(db, user_id, project_id)  # ownership check
    task = Task(project_id=project_id, **data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, user_id: int, task_id: int, data: TaskUpdate) -> Task:
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.user_id == user_id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, user_id: int, task_id: int) -> bool:
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.user_id == user_id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return True
