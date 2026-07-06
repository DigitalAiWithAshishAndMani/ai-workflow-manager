
import os
from typing import List
from models import ProjectTask, TaskStatus
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _serialize_task(t: ProjectTask):
    return {
        "id": t.id,
        "name": t.name,
        "role": t.role,
        "status": t.status.value,
        "stage_name": t.stage_name,
        "stage_order": t.stage_order,
        "assignee": t.assignee,
        "notes": t.notes,
    }


def suggest_next_tasks(tasks: List[ProjectTask]):
    """
    LLM-powered assistant:
    - Receives full task list as structured context
    - Returns suggested next tasks + bottlenecks
    """

    if not tasks:
        return {
            "message": "No tasks found for this project.",
            "next_tasks": [],
            "bottlenecks": [],
            "llm_reasoning": "Project has no tasks yet.",
        }

    task_payload = [_serialize_task(t) for t in tasks]

    system_prompt = (
        "You are a workflow orchestration assistant for a Screendragon-like system. "
        "Given project tasks with stages, status, and roles, you must:\n"
        "1) Identify the next best tasks to work on.\n"
        "2) Detect bottlenecks (BLOCKED tasks).\n"
        "3) Explain your reasoning briefly for project managers.\n"
        "Return JSON with keys: next_tasks (list of task ids), bottlenecks (list of task ids), reasoning."
    )

    user_prompt = (
        "Here is the current project task list as JSON:\n"
        f"{task_payload}\n\n"
        "Respond strictly in JSON."
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = completion.choices[0].message.content
        import json

        llm_result = json.loads(content)

        id_to_task = {t.id: t for t in tasks}

        def to_view(task_id):
            t = id_to_task.get(task_id)
            if not t:
                return None
            return {
                "id": t.id,
                "name": t.name,
                "stage": t.stage_name,
                "status": t.status.value,
                "role": t.role,
            }

        next_tasks = [v for tid in llm_result.get("next_tasks", []) if (v := to_view(tid))]
        bottlenecks = [v for tid in llm_result.get("bottlenecks", []) if (v := to_view(tid))]

        return {
            "message": "LLM-generated suggestions.",
            "next_tasks": next_tasks,
            "bottlenecks": bottlenecks,
            "llm_reasoning": llm_result.get("reasoning", ""),
        }

    except Exception as e:
        # Fallback heuristic if LLM fails
        min_order = None
        candidates = []
        for t in tasks:
            if t.status in {TaskStatus.PENDING, TaskStatus.BLOCKED}:
                if min_order is None or t.stage_order < min_order:
                    min_order = t.stage_order

        if min_order is None:
            return {
                "message": "All tasks are completed or approved.",
                "next_tasks": [],
                "bottlenecks": [],
                "llm_reasoning": f"LLM error: {e}",
            }

        for t in tasks:
            if t.stage_order == min_order and t.status in {TaskStatus.PENDING, TaskStatus.BLOCKED}:
                candidates.append(t)

        bottlenecks = [t for t in tasks if t.status == TaskStatus.BLOCKED]

        return {
            "message": "Heuristic suggestions (LLM unavailable).",
            "next_tasks": [
                {"id": t.id, "name": t.name, "stage": t.stage_name, "status": t.status.value}
                for t in candidates
            ],
            "bottlenecks": [
                {"id": t.id, "name": t.name, "stage": t.stage_name, "status": t.status.value}
                for t in bottlenecks
            ],
            "llm_reasoning": f"LLM error: {e}",
        }
