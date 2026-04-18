from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User
from backend.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectOut,
    TaskCreate, TaskUpdate, TaskOut,
)
from backend.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_service.get_projects(db, current_user.id)


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.create_project(db, current_user.id, data)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.get_project(db, current_user.id, project_id)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.update_project(db, current_user.id, project_id, data)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.delete_project(db, current_user.id, project_id)


# --- Tasks ---

@router.post("/{project_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(
    project_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.create_task(db, current_user.id, project_id, data)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.update_task(db, current_user.id, task_id, data)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.delete_task(db, current_user.id, task_id)
