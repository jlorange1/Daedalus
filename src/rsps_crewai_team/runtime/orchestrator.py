from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rsps_crewai_team.runtime.agency import load_agency_workflows, workflow_levels
from rsps_crewai_team.runtime.settings import AGENCY_RUNS_DIR
from rsps_crewai_team.runtime.work_orders import create_work_order


STEP_STATUSES = {"pending", "ready", "queued", "running", "awaiting_review", "done", "blocked", "failed"}
CODE_STEP_IDS = {"implementation", "ops_sync"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_id(workflow_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{workflow_id}"


def _workflow_by_id(workflow_id: str) -> dict[str, Any]:
    for workflow in load_agency_workflows().get("workflows", []):
        if workflow.get("id") == workflow_id:
            return workflow
    raise ValueError(f"Unknown workflow: {workflow_id}")


def _manifest_path(run_id: str) -> Path:
    return AGENCY_RUNS_DIR / run_id / "manifest.json"


def read_manifest(run_id: str) -> dict[str, Any]:
    return json.loads(_manifest_path(run_id).read_text(encoding="utf-8"))


def write_manifest(manifest: dict[str, Any]) -> Path:
    path = _manifest_path(str(manifest["run_id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def create_workflow_run(workflow_id: str, title: str | None = None) -> dict[str, Any]:
    workflow = _workflow_by_id(workflow_id)
    run_id = _run_id(workflow_id)
    levels = workflow_levels(workflow)
    first_ready = set(levels[0]) if levels else set()
    steps = {}
    for step in workflow.get("steps", []):
        step_id = str(step["id"])
        writes_code = step_id in CODE_STEP_IDS or step.get("department") == "backend_engineering"
        steps[step_id] = {
            "id": step_id,
            "department": step["department"],
            "depends_on": step.get("depends_on", []),
            "output": step.get("output", ""),
            "task": step.get("task", ""),
            "writes_code": writes_code,
            "approval_status": "approved",
            "status": "ready" if step_id in first_ready else "pending",
            "work_order": None,
        }
    manifest = {
        "run_id": run_id,
        "workflow_id": workflow_id,
        "workflow_name": workflow.get("name", workflow_id),
        "title": title or workflow.get("name", workflow_id),
        "status": "active",
        "created_at": _now(),
        "updated_at": _now(),
        "levels": levels,
        "steps": steps,
    }
    write_manifest(manifest)
    enqueue_ready_steps(run_id)
    return read_manifest(run_id)


def enqueue_ready_steps(run_id: str) -> dict[str, Any]:
    manifest = read_manifest(run_id)
    for step in manifest["steps"].values():
        if step["status"] != "ready" or step.get("work_order"):
            continue
        metadata = {
            "workflow_id": manifest["workflow_id"],
            "run_id": manifest["run_id"],
            "step_id": step["id"],
            "department": step["department"],
            "writes_code": step["writes_code"],
            "approval_status": step["approval_status"],
        }
        body = (
            f"Workflow: {manifest['workflow_name']}\n"
            f"Run: {manifest['run_id']}\n"
            f"Department: {step['department']}\n"
            f"Expected output: {step['output']}\n\n"
            f"{step['task']}\n"
        )
        path = create_work_order(f"{manifest['workflow_name']}: {step['id']}", body, metadata=metadata)
        step["work_order"] = str(path)
        step["status"] = "queued"
    manifest["updated_at"] = _now()
    write_manifest(manifest)
    return manifest


def _refresh_ready_steps(manifest: dict[str, Any]) -> None:
    steps = manifest.get("steps", {})
    for step in steps.values():
        if step.get("status") != "pending":
            continue
        dependencies = step.get("depends_on", [])
        if all(steps.get(dep, {}).get("status") == "done" for dep in dependencies):
            step["status"] = "ready"


def update_step_status(
    run_id: str,
    step_id: str,
    status: str,
    *,
    detail: str | None = None,
    worker_run_id: str | None = None,
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in STEP_STATUSES:
        raise ValueError(f"Unknown workflow step status: {status}")
    manifest = read_manifest(run_id)
    steps = manifest.get("steps", {})
    if step_id not in steps:
        raise ValueError(f"Unknown workflow step for {run_id}: {step_id}")
    step = steps[step_id]
    step["status"] = status
    step["updated_at"] = _now()
    if detail:
        step["detail"] = detail[-1000:]
    if worker_run_id:
        step["worker_run_id"] = worker_run_id
    if artifact:
        step["artifact"] = artifact
    if status == "done":
        _refresh_ready_steps(manifest)
    if any(item.get("status") in {"failed", "blocked"} for item in steps.values()):
        manifest["status"] = "blocked"
    elif all(item.get("status") == "done" for item in steps.values()):
        manifest["status"] = "done"
    else:
        manifest["status"] = "active"
    manifest["updated_at"] = _now()
    write_manifest(manifest)
    return enqueue_ready_steps(run_id)


def approve_step(run_id: str, step_id: str) -> dict[str, Any]:
    manifest = read_manifest(run_id)
    steps = manifest.get("steps", {})
    if step_id not in steps:
        raise ValueError(f"Unknown workflow step for {run_id}: {step_id}")
    step = steps[step_id]
    step["approval_status"] = "approved"
    if step.get("status") == "awaiting_review":
        step["status"] = "ready"
    step["updated_at"] = _now()
    manifest["updated_at"] = _now()
    write_manifest(manifest)
    return enqueue_ready_steps(run_id)


def advance_from_work_order(
    metadata: dict[str, Any] | None,
    final_status: str,
    *,
    detail: str | None = None,
    worker_run_id: str | None = None,
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not metadata:
        return None
    run_id = metadata.get("run_id")
    step_id = metadata.get("step_id") or metadata.get("workflow_step_id")
    if not run_id or not step_id:
        return None
    status = "done" if final_status == "done" else "failed"
    return update_step_status(str(run_id), str(step_id), status, detail=detail, worker_run_id=worker_run_id, artifact=artifact)


def list_workflow_runs(limit: int = 5) -> list[dict[str, Any]]:
    if not AGENCY_RUNS_DIR.exists():
        return []
    manifests = sorted(AGENCY_RUNS_DIR.glob("*/manifest.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    runs = []
    for path in manifests[:limit]:
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        steps = list(manifest.get("steps", {}).values())
        runs.append(
            {
                "run_id": manifest.get("run_id"),
                "workflow_id": manifest.get("workflow_id"),
                "workflow_name": manifest.get("workflow_name"),
                "title": manifest.get("title"),
                "status": manifest.get("status"),
                "updated_at": manifest.get("updated_at"),
                "step_count": len(steps),
                "queued": sum(1 for step in steps if step.get("status") == "queued"),
                "done": sum(1 for step in steps if step.get("status") == "done"),
                "blocked": sum(1 for step in steps if step.get("status") in {"blocked", "failed"}),
                "steps": steps,
            }
        )
    return runs
