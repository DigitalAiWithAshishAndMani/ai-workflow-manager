# AI Workflow Manager

A FastAPI-based workflow manager with LLM-assisted task suggestions.

## Features

- Create workflow templates (stages + tasks)
- Instantiate projects from templates
- Assign tasks, update status, track approvals
- LLM assistant to suggest next tasks and detect bottlenecks

## Quick start (local)

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
