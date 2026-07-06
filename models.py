
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
    APPROVED = "APPROVED"


class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)

    stages = relationship("WorkflowStage", back_populates="template", cascade="all, delete-orphan")


class WorkflowStage(Base):
    __tablename__ = "workflow_stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    order = Column(Integer, index=True)

    template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    template = relationship("WorkflowTemplate", back_populates="stages")

    tasks = relationship("WorkflowTaskTemplate", back_populates="stage", cascade="all, delete-orphan")


class WorkflowTaskTemplate(Base):
    __tablename__ = "workflow_task_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    stage_id = Column(Integer, ForeignKey("workflow_stages.id"))
    stage = relationship("WorkflowStage", back_populates="tasks")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    client = Column(String, nullable=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"))

    template = relationship("WorkflowTemplate")
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")


class ProjectTask(Base):
    __tablename__ = "project_tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    assignee = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    stage_name = Column(String, index=True)
    stage_order = Column(Integer, index=True)

    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="tasks")
