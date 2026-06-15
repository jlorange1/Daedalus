from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from rsps_crewai_team.runtime.settings import WORK_ORDERS_DIR


STATUS_DIRS = ("inbox", "running", "done", "failed")


@dataclass(frozen=True)
class WorkOrder:
    path: Path
    title: str
    body: str


def ensure_work_order_dirs() -> None:
    for status in STATUS_DIRS:
        (WORK_ORDERS_DIR / status).mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:64] or "work-order"


def create_work_order(title: str, body: str) -> Path:
    ensure_work_order_dirs()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = WORK_ORDERS_DIR / "inbox" / f"{timestamp}-{slugify(title)}.md"
    content = f"# {title.strip()}\n\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")
    return path


def next_work_order() -> WorkOrder | None:
    ensure_work_order_dirs()
    candidates = sorted((WORK_ORDERS_DIR / "inbox").glob("*.md"))
    if not candidates:
        return None
    path = candidates[0]
    body = path.read_text(encoding="utf-8")
    title = path.stem
    for line in body.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return WorkOrder(path=path, title=title, body=body)


def move_work_order(order: WorkOrder, status: str) -> Path:
    if status not in STATUS_DIRS:
        raise ValueError(f"Unknown work-order status: {status}")
    ensure_work_order_dirs()
    destination = WORK_ORDERS_DIR / status / order.path.name
    order.path.replace(destination)
    return destination
