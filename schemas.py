from pydantic import BaseModel
from typing import List, Optional
from models import TaskStatus


class WorkflowTaskTemplateCreate(BaseModel):
    name: str
    role: Optional[str] = None
    description: Optional[str] = None


class WorkflowStageCreate(BaseModel):
    name: str
    order: int
    tasks: List[WorkflowTaskTemplateCreate]


class WorkflowTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    stages: List[WorkflowStageCreate]


class WorkflowTemplateRead(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    client: Optional[str] = None
    template_id: int


class ProjectTaskRead(BaseModel):
    id: int
    name: str
    role: Optional[str]
    description: Optional[str]
    status: TaskStatus
    assignee: Optional[str]
    notes: Optional[str]
    stage_name: str
    stage_order: int

    class Config:
        from_attributes = True


class ProjectRead(BaseModel):
    id: int
    name: str
    client: Optional[str]
    template_id: int
    tasks: List[ProjectTaskRead]

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    assignee: Optional[str] = None
    notes: Optional[str] = None
