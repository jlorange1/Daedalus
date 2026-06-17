from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
CATALOG_PATH = CONFIG_DIR / "agency_catalog.json"
WORKFLOWS_PATH = CONFIG_DIR / "agency_workflows.json"


@dataclass(frozen=True)
class WorkflowDag:
    workflow_id: str
    levels: list[list[str]]
    step_count: int
    max_parallel: int


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_agency_catalog() -> dict[str, Any]:
    return _load_json(CATALOG_PATH)


def load_agency_workflows() -> dict[str, Any]:
    return _load_json(WORKFLOWS_PATH)


def department_ids(catalog: dict[str, Any] | None = None) -> set[str]:
    data = catalog if catalog is not None else load_agency_catalog()
    return {str(item["id"]) for item in data.get("departments", [])}


def workflow_levels(workflow: dict[str, Any]) -> list[list[str]]:
    steps = workflow.get("steps", [])
    step_ids = {str(step["id"]) for step in steps}
    remaining = set(step_ids)
    dependencies = {
        str(step["id"]): {str(dep) for dep in step.get("depends_on", [])}
        for step in steps
    }
    unknown = {
        step_id: sorted(deps - step_ids)
        for step_id, deps in dependencies.items()
        if deps - step_ids
    }
    if unknown:
        details = ", ".join(f"{step}: {deps}" for step, deps in sorted(unknown.items()))
        raise ValueError(f"workflow {workflow.get('id', '<unknown>')} has unknown dependencies: {details}")

    levels: list[list[str]] = []
    completed: set[str] = set()
    while remaining:
        level = sorted(step_id for step_id in remaining if dependencies[step_id] <= completed)
        if not level:
            raise ValueError(f"workflow {workflow.get('id', '<unknown>')} has a dependency cycle")
        levels.append(level)
        completed.update(level)
        remaining.difference_update(level)
    return levels


def validate_agency_config() -> list[WorkflowDag]:
    catalog = load_agency_catalog()
    workflows = load_agency_workflows()
    departments = department_ids(catalog)
    if not departments:
        raise ValueError("agency catalog has no departments")

    dags: list[WorkflowDag] = []
    for workflow in workflows.get("workflows", []):
        for step in workflow.get("steps", []):
            department = str(step.get("department", ""))
            if department not in departments:
                raise ValueError(f"workflow {workflow.get('id')} references unknown department {department}")
        levels = workflow_levels(workflow)
        dags.append(
            WorkflowDag(
                workflow_id=str(workflow["id"]),
                levels=levels,
                step_count=len(workflow.get("steps", [])),
                max_parallel=max((len(level) for level in levels), default=0),
            )
        )
    if not dags:
        raise ValueError("agency workflow config has no workflows")
    return dags


def agency_status() -> dict[str, Any]:
    catalog = load_agency_catalog()
    workflows = load_agency_workflows()
    dags = validate_agency_config()
    department_count = len(catalog.get("departments", []))
    workflow_summaries = []
    workflows_by_id = {str(item["id"]): item for item in workflows.get("workflows", [])}
    for dag in dags:
        workflow = workflows_by_id[dag.workflow_id]
        workflow_summaries.append(
            {
                "id": dag.workflow_id,
                "name": workflow.get("name", dag.workflow_id),
                "description": workflow.get("description", ""),
                "concurrency": workflow.get("concurrency", dag.max_parallel),
                "step_count": dag.step_count,
                "levels": dag.levels,
                "max_parallel": dag.max_parallel,
            }
        )
    return {
        "source": catalog.get("source_inspiration", {}),
        "principles": catalog.get("principles", []),
        "department_count": department_count,
        "workflow_count": len(workflow_summaries),
        "departments": catalog.get("departments", []),
        "workflows": workflow_summaries,
    }
