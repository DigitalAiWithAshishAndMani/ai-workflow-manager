from fastapi import FastAPI
from database import Base, engine
from routers import workflows, projects

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Workflow Manager")

app.include_router(workflows.router)
app.include_router(projects.router)


@app.get("/")
def root():
    return {"message": "AI Workflow Manager is running"}
