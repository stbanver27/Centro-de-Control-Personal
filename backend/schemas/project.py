from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend.models.project import TaskStatus, Priority


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    priority: Priority = Priority.medium
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None


class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: Priority
    due_date: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#6366f1"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    created_at: datetime
    tasks: List[TaskOut] = []
    progress: float = 0.0

    model_config = {"from_attributes": True}
