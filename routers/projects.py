
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Project, WorkflowTemplate, ProjectTask, TaskStatus
from schemas import ProjectCreate, ProjectRead, TaskUpdate, ProjectTaskRead
from ai_assistant import suggest_next_tasks

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    template = db.query(WorkflowTemplate).filter(WorkflowTemplate.id == payload.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    project = Project(name=payload.name, client=payload.client, template=template)
    db.add(project)
    db.flush()

    for stage in template.stages:
        for task_template in stage.tasks:
            task = ProjectTask(
                name=task_template.name,
                role=task_template.role,
                description=task_template.description,
                status=TaskStatus.PENDING,
                stage_name=stage.name,
                stage_order=stage.order,
                project=project,
            )
            db.add(task)

    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}/tasks/{task_id}", response_model=ProjectTaskRead)
def update_task(project_id: int, task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = (
        db.query(ProjectTask)
        .filter(ProjectTask.id == task_id, ProjectTask.project_id == project_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.status is not None:
        task.status = payload.status
    if payload.assignee is not None:
        task.assignee = payload.assignee
    if payload.notes is not None:
        task.notes = payload.notes

    db.commit()
    db.refresh(task)
    return task


@router.get("/{project_id}/ai/suggestions")
def get_ai_suggestions(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    suggestions = suggest_next_tasks(project.tasks)
    return suggestions
