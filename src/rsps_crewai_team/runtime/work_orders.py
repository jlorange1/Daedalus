from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rsps_crewai_team.runtime.settings import WORK_ORDERS_DIR


STATUS_DIRS = ("inbox", "running", "done", "failed")


@dataclass(frozen=True)
class WorkOrder:
    path: Path
    title: str
    body: str
    metadata: dict[str, Any] | None = None


def ensure_work_order_dirs() -> None:
    for status in STATUS_DIRS:
        (WORK_ORDERS_DIR / status).mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:64] or "work-order"


def metadata_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".meta.json")


def read_work_order_metadata(path: Path) -> dict[str, Any]:
    sidecar = metadata_path(path)
    if not sidecar.exists():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_work_order_metadata(path: Path, metadata: dict[str, Any]) -> Path:
    sidecar = metadata_path(path)
    sidecar.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sidecar


def validate_workflow_metadata(workflow_id: str | None, workflow_step_id: str | None) -> dict[str, Any]:
    if not workflow_id and not workflow_step_id:
        return {}
    from rsps_crewai_team.runtime.agency import load_agency_workflows

    workflows = load_agency_workflows().get("workflows", [])
    workflow = next((item for item in workflows if item.get("id") == workflow_id), None)
    if workflow is None:
        raise ValueError(f"Unknown workflow_id: {workflow_id}")
    step = None
    if workflow_step_id:
        step = next((item for item in workflow.get("steps", []) if item.get("id") == workflow_step_id), None)
        if step is None:
            raise ValueError(f"Unknown workflow_step_id for {workflow_id}: {workflow_step_id}")
    return {
        "workflow_id": workflow_id,
        "workflow_step_id": workflow_step_id,
        "workflow_department": step.get("department") if step else None,
    }


def parse_work_order_text(text: str, fallback_title: str) -> tuple[str, str, dict[str, Any] | None]:
    metadata = None
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            raw = text[4:end].strip()
            body = text[end + 5 :]
            if raw:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    metadata = parsed
    title = fallback_title
    for line in body.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return title, body, metadata


def create_work_order(title: str, body: str, metadata: dict[str, Any] | None = None) -> Path:
    ensure_work_order_dirs()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = WORK_ORDERS_DIR / "inbox" / f"{timestamp}-{slugify(title)}.md"
    content = f"# {title.strip()}\n\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")
    if metadata:
        write_work_order_metadata(path, metadata)
    return path


def read_work_order(path: Path) -> WorkOrder:
    text = path.read_text(encoding="utf-8")
    title, body, metadata = parse_work_order_text(text, path.stem)
    sidecar = read_work_order_metadata(path)
    if sidecar:
        metadata = {**(metadata or {}), **sidecar}
    return WorkOrder(path=path, title=title, body=body, metadata=metadata)


def work_order_approved_for_worker(order: WorkOrder) -> bool:
    metadata = order.metadata or {}
    if not metadata:
        return True
    if not metadata.get("writes_code", False):
        return True
    return metadata.get("approval_status") == "approved"


def next_work_order(approved_only: bool = False) -> WorkOrder | None:
    ensure_work_order_dirs()
    candidates = sorted((WORK_ORDERS_DIR / "inbox").glob("*.md"))
    for path in candidates:
        order = read_work_order(path)
        if not approved_only or work_order_approved_for_worker(order):
            return order
    return None


def move_work_order(order: WorkOrder, status: str) -> Path:
    if status not in STATUS_DIRS:
        raise ValueError(f"Unknown work-order status: {status}")
    ensure_work_order_dirs()
    destination = WORK_ORDERS_DIR / status / order.path.name
    source_meta = metadata_path(order.path)
    destination_meta = metadata_path(destination)
    order.path.replace(destination)
    if source_meta.exists():
        source_meta.replace(destination_meta)
    return destination
