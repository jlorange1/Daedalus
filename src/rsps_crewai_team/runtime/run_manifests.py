from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rsps_crewai_team.runtime.settings import LOGS_DIR


RUNS_DIR = LOGS_DIR / "runs"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def manifest_path(run_id: str) -> Path:
    return RUNS_DIR / f"{run_id}.json"


def create_run_manifest(run_id: str, **fields: Any) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "status": fields.pop("status", "running"),
        "started_at": fields.pop("started_at", now_iso()),
        "updated_at": now_iso(),
        **fields,
    }
    path = manifest_path(run_id)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def update_run_manifest(run_id: str, **fields: Any) -> Path:
    path = manifest_path(run_id)
    payload: dict[str, Any] = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                payload = loaded
        except json.JSONDecodeError:
            payload = {}
    payload.update(fields)
    payload["run_id"] = run_id
    payload["updated_at"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def recent_run_manifests(limit: int = 8) -> list[dict[str, Any]]:
    if not RUNS_DIR.exists():
        return []
    manifests = sorted(RUNS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    rows: list[dict[str, Any]] = []
    for path in manifests[:limit]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            rows.append(data)
    return rows
