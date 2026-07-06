from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import WorkflowTemplate, WorkflowStage, WorkflowTaskTemplate
from schemas import WorkflowTemplateCreate, WorkflowTemplateRead

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowTemplateRead)
def create_workflow_template(payload: WorkflowTemplateCreate, db: Session = Depends(get_db)):
    existing = db.query(WorkflowTemplate).filter(WorkflowTemplate.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Template with this name already exists")

    template = WorkflowTemplate(name=payload.name, description=payload.description)
    db.add(template)
    db.flush()

    for stage_data in payload.stages:
        stage = WorkflowStage(
            name=stage_data.name,
            order=stage_data.order,
            template=template,
        )
        db.add(stage)
        db.flush()
        for task_data in stage_data.tasks:
            task = WorkflowTaskTemplate(
                name=task_data.name,
                role=task_data.role,
                description=task_data.description,
                stage=stage,
            )
            db.add(task)

    db.commit()
    db.refresh(template)
    return template


@router.get("/", response_model=list[WorkflowTemplateRead])
def list_workflow_templates(db: Session = Depends(get_db)):
    return db.query(WorkflowTemplate).all()
