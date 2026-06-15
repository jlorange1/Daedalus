from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORK_ORDERS_DIR = PROJECT_ROOT / "work_orders"
LOGS_DIR = PROJECT_ROOT / "logs"


def bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def rsps_repo_path() -> Path:
    raw_path = os.getenv("RSPS_REPO_PATH", "").strip()
    if not raw_path:
        raise RuntimeError("RSPS_REPO_PATH is not set.")
    path = Path(raw_path).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise RuntimeError(f"RSPS_REPO_PATH does not exist or is not a directory: {path}")
    return path


def require_autonomy_enabled() -> None:
    if not bool_env("RSPS_ALLOW_AUTONOMOUS", False):
        raise RuntimeError(
            "Autonomous execution is disabled. Set RSPS_ALLOW_AUTONOMOUS=true to let "
            "the worker modify the RSPS repo."
        )
