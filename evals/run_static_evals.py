#!/usr/bin/env python3
"""Safe local static evals for Daedalus orchestration quality."""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "evals" / "results"


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    elapsed_ms: int


def _timed(name: str, check: Callable[[], tuple[bool, str]]) -> CheckResult:
    start = time.perf_counter()
    try:
        ok, detail = check()
    except Exception as exc:  # pragma: no cover - defensive report path
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return CheckResult(name=name, ok=ok, detail=detail, elapsed_ms=elapsed_ms)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def check_required_paths() -> tuple[bool, str]:
    required = [
        "docs/EVALS.md",
        "docs/SAFETY_BOUNDARIES.md",
        "docs/ORCHESTRATION.md",
        "evals/README.md",
        "memory/TASK_GRAPH.md",
        "memory/DECISIONS.md",
        "memory/FAILED_ATTEMPTS.md",
        "work_orders/inbox",
        "work_orders/running",
        "work_orders/done",
        "work_orders/failed",
        "src/rsps_crewai_team/worker.py",
        "src/rsps_crewai_team/dashboard.py",
        "src/rsps_crewai_team/runtime/agency.py",
        "src/rsps_crewai_team/config/agency_catalog.json",
        "src/rsps_crewai_team/config/agency_workflows.json",
        "docs/AGENCY_AGENTS_INTEGRATION.md",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        return False, "missing: " + ", ".join(missing)
    return True, f"{len(required)} required paths present"


def check_task_graph() -> tuple[bool, str]:
    text = _read(ROOT / "memory" / "TASK_GRAPH.md")
    required_terms = ["| ID |", "Dependencies", "Owner", "Status", "Risk"]
    missing = [term for term in required_terms if term not in text]
    task_rows = [line for line in text.splitlines() if line.startswith("|") and line.count("|") >= 6]
    data_rows = [line for line in task_rows if not line.startswith("|---") and "| ID |" not in line]
    if missing:
        return False, "missing task graph terms: " + ", ".join(missing)
    if len(data_rows) < 3:
        return False, f"expected at least 3 task rows, found {len(data_rows)}"
    return True, f"{len(data_rows)} task rows with dependency/status/risk columns"


def check_failed_attempts_memory() -> tuple[bool, str]:
    text = _read(ROOT / "memory" / "FAILED_ATTEMPTS.md")
    required_terms = ["Attempt:", "Failure:", "Lesson:"]
    missing = [term for term in required_terms if term not in text]
    if missing:
        return False, "missing recovery terms: " + ", ".join(missing)
    return True, "failed-attempt memory records attempt, failure, and lesson"


def check_safety_boundaries() -> tuple[bool, str]:
    text = _read(ROOT / "docs" / "SAFETY_BOUNDARIES.md").lower()
    disallowed = ["exploit", "credential", "malware", "evasion", "unauthorized"]
    fallbacks = ["defensive checklist", "safe mock", "human approval request", "smaller scoped implementation"]
    missing = [term for term in disallowed + fallbacks if term not in text]
    if missing:
        return False, "missing safety terms: " + ", ".join(missing)
    worker = _read(ROOT / "src" / "rsps_crewai_team" / "worker.py")
    if "require_autonomy_enabled()" not in worker:
        return False, "worker does not visibly require autonomy gate before running work"
    return True, "safety boundaries and worker autonomy gate present"


def check_python_source_parses() -> tuple[bool, str]:
    failures: list[str] = []
    for path in sorted((ROOT / "src").rglob("*.py")):
        try:
            ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"{path.relative_to(ROOT)}:{exc.lineno}")
    if failures:
        return False, "syntax failures: " + ", ".join(failures)
    return True, "all src Python files parse with ast"


def check_json_assets_parse() -> tuple[bool, str]:
    roots = [ROOT / "src", ROOT / "evals"]
    json_files = [path for base in roots for path in base.rglob("*.json")]
    failures: list[str] = []
    for path in sorted(json_files):
        try:
            json.loads(_read(path))
        except json.JSONDecodeError as exc:
            failures.append(f"{path.relative_to(ROOT)}:{exc.lineno}")
    if failures:
        return False, "JSON parse failures: " + ", ".join(failures)
    return True, f"{len(json_files)} JSON files parse"


def check_agency_config() -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    script = (
        "from rsps_crewai_team.runtime.agency import agency_status;"
        "s=agency_status();"
        "assert s['department_count'] >= 14;"
        "assert s['workflow_count'] >= 3;"
        "assert any(w['id']=='feature_delivery_mesh' for w in s['workflows']);"
        "print(f\"{s['department_count']} departments, {s['workflow_count']} workflows\")"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    if result.returncode != 0:
        return False, f"agency config failed: {output[-500:]}"
    return True, output.strip()


def check_worker_status_latency() -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-m", "rsps_crewai_team.worker", "status"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    if result.returncode != 0:
        return False, f"worker status failed in {elapsed_ms}ms: {output[-500:]}"
    if elapsed_ms > 5000:
        return False, f"worker status exceeded 5000ms budget: {elapsed_ms}ms"
    return True, f"worker status completed in {elapsed_ms}ms"


def run_checks() -> dict[str, object]:
    checks = [
        ("required_paths", check_required_paths),
        ("task_graph", check_task_graph),
        ("failed_attempts_memory", check_failed_attempts_memory),
        ("safety_boundaries", check_safety_boundaries),
        ("python_source_parses", check_python_source_parses),
        ("json_assets_parse", check_json_assets_parse),
        ("agency_config", check_agency_config),
        ("worker_status_latency", check_worker_status_latency),
    ]
    started = datetime.now(timezone.utc)
    results = [_timed(name, check) for name, check in checks]
    total_elapsed_ms = sum(item.elapsed_ms for item in results)
    return {
        "suite": "daedalus_static_evals",
        "started_at": started.isoformat(),
        "root": str(ROOT),
        "ok": all(item.ok for item in results) and total_elapsed_ms <= 10_000,
        "latency_budget_ms": 10_000,
        "total_elapsed_ms": total_elapsed_ms,
        "checks": [item.__dict__ for item in results],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run safe local Daedalus static evals.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON report under evals/results.")
    args = parser.parse_args()

    report = run_checks()
    print(json.dumps(report, indent=2))

    if args.write_report:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = RESULTS_DIR / f"static-evals-{stamp}.json"
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"report={path}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
